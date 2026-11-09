from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
import urllib.parse
from pathlib import Path


EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def capture(base: str, token: str, output: Path, section: str, size: tuple[int, int], conversation: str | None = None) -> None:
    output = output.resolve()
    query = {"section": section}
    if conversation:
        query["conversation"] = conversation
    url = f"{base}/?{urllib.parse.urlencode(query)}#token={token}"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cache-north-edge-", ignore_cleanup_errors=True) as profile:
        result = subprocess.run(
            [
                str(EDGE),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-first-run",
                "--disable-default-apps",
                f"--user-data-dir={profile}",
                f"--window-size={size[0]},{size[1]}",
                "--virtual-time-budget=12000",
                f"--screenshot={output}",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or f"Edge exited with {result.returncode}")
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and (not output.is_file() or output.stat().st_size < 10_000):
        time.sleep(0.1)
    if not output.is_file() or output.stat().st_size < 10_000:
        raise RuntimeError(f"Screenshot was not created correctly: {output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    parser.add_argument("--evaluation", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not EDGE.is_file():
        raise SystemExit("Microsoft Edge is unavailable.")
    session = json.loads(Path(args.session).read_text(encoding="utf-8"))
    evaluation = json.loads(Path(args.evaluation).read_text(encoding="utf-8"))
    base, token = session["url"].split("/#token=", 1)
    checks = {str(item["id"]): item for item in evaluation["checks"]}
    destination = Path(args.output)
    jobs = (
        ("02-ai-chat.png", "chat", (1920, 1080), checks["1"]["conversation_id"]),
        ("03-knowledge-library.png", "library", (1920, 1080), None),
        ("04-document-search.png", "documents", (1920, 1080), None),
        ("05-document-answer-citations.png", "chat", (1920, 1080), checks["5"]["conversation_id"]),
        ("06-offline-maps.png", "maps", (1920, 1080), None),
        ("07-settings.png", "settings", (1920, 1080), None),
        ("08-system-status.png", "status", (1920, 1080), None),
        ("09-responsive-1366x768.png", "chat", (1366, 768), checks["2"]["conversation_id"]),
        ("10-guides.png", "guides", (1920, 1080), None),
    )
    for name, section, size, conversation in jobs:
        capture(base, token, destination / name, section, size, conversation)
        print(f"captured {name} at {size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
