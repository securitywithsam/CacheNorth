from __future__ import annotations

import argparse
import json
import logging
import os
import threading
import time
import webbrowser
from pathlib import Path

from waitress import create_server
import psutil

from .acceleration import start_engine
from .app import create_app
from .config import discover_paths
from .engine import EngineError, KoboldEngine, find_free_port
from .settings import SettingsStore
from .models import ModelManager


class RuntimeController:
    def __init__(
        self,
        root: str | None,
        headless: bool = False,
        start_engine: bool = True,
        session_file: str | None = None,
        parent_pid: int | None = None,
    ):
        self.paths = discover_paths(root)
        self.paths.ensure_writable_data()
        self.headless = headless
        self.start_engine_enabled = start_engine
        self.engine = KoboldEngine(self.paths, self._engine_status)
        self.settings = SettingsStore(self.paths.data / "settings.json")
        self.models = ModelManager(self.paths.models, self.settings)
        selected = self.models.selected()
        if selected:
            self.engine.set_model(selected.name)
        self.app, self.state = create_app(self.paths, self.engine)
        self.port = find_free_port()
        self.server = create_server(self.app, host="127.0.0.1", port=self.port, threads=8)
        self.server_thread: threading.Thread | None = None
        self.root_window = None
        self.status_variable = None
        self.brand_image = None
        self.session_file = Path(session_file).resolve() if session_file else None
        self.parent_pid = parent_pid
        self._closing = threading.Event()
        self._shutdown_complete = threading.Event()
        self.state.shutdown_callback = self.shutdown

    @property
    def dashboard_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/#token={self.state.token}"

    def _engine_status(self, _state: str, message: str) -> None:
        if self.status_variable is not None and self.root_window is not None:
            self.root_window.after(0, lambda: self.status_variable.set(message))

    def _start_engine(self) -> None:
        if not self.start_engine_enabled:
            self._engine_status("stopped", "AI engine start skipped for this session.")
            return
        try:
            # CPU is the default; GPU applies only if chosen on this computer and not previously failed here.
            start_engine(self.engine, self.settings)
        except EngineError as exc:
            logging.exception("AI engine startup failed")
            self._engine_status("error", str(exc))

    def start_server(self) -> None:
        self.server_thread = threading.Thread(target=self.server.run, name="local-dashboard", daemon=True)
        self.server_thread.start()
        threading.Thread(target=self._startup_content_scan, name="startup-content-scan", daemon=True).start()

    def _startup_content_scan(self) -> None:
        """Incrementally discover files copied beside the app without delaying the dashboard."""
        try:
            self.app.extensions["sws"]["documents"].sync_folder()
        except Exception:
            logging.exception("Startup document scan failed; existing index records were preserved")

    def publish_session(self) -> None:
        if self.session_file is None:
            return
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.session_file.with_suffix(self.session_file.suffix + ".tmp")
        temporary.write_text(
            json.dumps({"url": self.dashboard_url, "pid": os.getpid(), "root": str(self.paths.root)}),
            encoding="utf-8",
        )
        temporary.replace(self.session_file)

    def monitor_parent(self) -> None:
        if not self.parent_pid:
            return
        while not self._closing.wait(1.0):
            if not psutil.pid_exists(self.parent_pid):
                self.shutdown()
                return

    def open_dashboard(self) -> None:
        webbrowser.open(self.dashboard_url, new=1)

    def run_headless(self) -> int:
        self.start_server()
        self.publish_session()
        print(self.dashboard_url, flush=True)
        if self.parent_pid:
            threading.Thread(target=self.monitor_parent, name="shell-parent-monitor", daemon=True).start()
        if self.start_engine_enabled:
            threading.Thread(target=self._start_engine, name="ai-engine-start", daemon=True).start()
        try:
            while not self._closing.wait(0.5):
                pass
        except KeyboardInterrupt:
            self.shutdown()
        # API shutdown runs on a daemon request thread. Keep the packaged process alive
        # until that thread has stopped the engine and removed the session file.
        self._shutdown_complete.wait(30)
        return 0

    def run_gui(self) -> int:
        import tkinter as tk
        from tkinter import messagebox, ttk

        window = tk.Tk()
        self.root_window = window
        window.title("CacheNorth by Security With Sam")
        window.geometry("620x310")
        window.minsize(580, 290)
        window.configure(bg="#08111f")
        window.protocol("WM_DELETE_WINDOW", self.shutdown)

        style = ttk.Style(window)
        style.theme_use("clam")
        style.configure("SWS.TFrame", background="#08111f")
        style.configure("SWS.TLabel", background="#08111f", foreground="#dceaff", font=("Segoe UI", 10))
        style.configure("Title.SWS.TLabel", background="#08111f", foreground="#ffffff", font=("Segoe UI Semibold", 18))
        style.configure("SWS.TButton", font=("Segoe UI Semibold", 10), padding=(16, 9))

        frame = ttk.Frame(window, style="SWS.TFrame", padding=28)
        frame.pack(fill="both", expand=True)
        brand_row = ttk.Frame(frame, style="SWS.TFrame")
        brand_row.pack(fill="x")
        logo_path = self.paths.dashboard / "cache-north-logo.png"
        if logo_path.is_file():
            try:
                self.brand_image = tk.PhotoImage(file=str(logo_path)).subsample(3, 3)
                ttk.Label(brand_row, image=self.brand_image, style="SWS.TLabel").pack(side="left", padx=(0, 16))
            except tk.TclError:
                self.brand_image = None
        brand_copy = ttk.Frame(brand_row, style="SWS.TFrame")
        brand_copy.pack(side="left", fill="x", expand=True)
        ttk.Label(brand_copy, text="SECURITY WITH SAM", style="SWS.TLabel").pack(anchor="w")
        ttk.Label(brand_copy, text="CacheNorth", style="Title.SWS.TLabel").pack(anchor="w", pady=(3, 1))
        ttk.Label(brand_copy, text="Your knowledge. Anywhere.", style="SWS.TLabel").pack(anchor="w")
        self.status_variable = tk.StringVar(value="Starting local dashboard...")
        ttk.Label(frame, textvariable=self.status_variable, style="SWS.TLabel", wraplength=490).pack(anchor="w")
        progress = ttk.Progressbar(frame, mode="indeterminate")
        progress.pack(fill="x", pady=(14, 22))
        progress.start(14)
        controls = ttk.Frame(frame, style="SWS.TFrame")
        controls.pack(fill="x")
        ttk.Button(controls, text="Open Dashboard", style="SWS.TButton", command=self.open_dashboard).pack(side="left")
        ttk.Button(controls, text="Exit", style="SWS.TButton", command=self.shutdown).pack(side="right")

        try:
            self.start_server()
            self.status_variable.set("Dashboard ready. Starting the CPU-compatible AI engine...")
            self.open_dashboard()
            threading.Thread(target=self._start_engine, name="ai-engine-start", daemon=True).start()
            window.mainloop()
        except Exception as exc:
            logging.exception("Application startup failed")
            messagebox.showerror("CacheNorth could not start", str(exc))
            self.shutdown()
            return 1
        return 0

    def shutdown(self) -> None:
        if self._closing.is_set():
            return
        self._closing.set()
        try:
            self.engine.stop()
        finally:
            try:
                try:
                    self.server.close()
                except Exception:
                    pass
                if self.root_window is not None:
                    try:
                        self.root_window.after(0, self.root_window.destroy)
                    except Exception:
                        pass
                if self.session_file is not None:
                    try:
                        self.session_file.unlink(missing_ok=True)
                    except OSError:
                        pass
            finally:
                self._shutdown_complete.set()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CacheNorth by Security With Sam")
    parser.add_argument("--root", help="Release or USB root. Auto-detected in packaged builds.")
    parser.add_argument("--headless", action="store_true", help="Run without the controller window.")
    parser.add_argument("--no-engine", action="store_true", help="Start the dashboard without KoboldCpp.")
    parser.add_argument("--session-file", help="Write the local dashboard URL for the native shell.")
    parser.add_argument("--parent-pid", type=int, help="Stop if the native shell process exits.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        controller = RuntimeController(
            args.root,
            headless=args.headless,
            start_engine=not args.no_engine,
            session_file=args.session_file,
            parent_pid=args.parent_pid,
        )
    except Exception as exc:
        if args.headless:
            raise
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("CacheNorth could not start", str(exc))
        root.destroy()
        return 1
    return controller.run_headless() if args.headless else controller.run_gui()
