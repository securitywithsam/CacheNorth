# CacheNorth architecture

```
Launch CacheNorth.exe  (C# WinForms + WebView2, launcher/StartOfflineAI.cs)
   │  starts, watches, and closes ──────────────────────────────┐
   ▼                                                            │
SecurityWithSamOfflineAI.exe  (Python backend, PyInstaller)     │ dashboard in the native window
   │  Flask app on waitress, 127.0.0.1:<random port>  ◄─────────┘ (or the default browser as fallback)
   │  • REST API, session token required          src/security_with_sam/app.py
   │  • document index (SQLite FTS5)               documents.py
   │  • conversation store (SQLite)                storage.py
   │  • model discovery (GGUF metadata)            models.py
   │  • GPU policy, per-computer settings          acceleration.py, settings.py
   │  • context planning and prompt fitting        context.py, prompting.py
   │  starts in a Windows Job Object
   ▼
KoboldCpp (unpacked, Apps\Offline AI\KoboldCpp)  — llama.cpp inference, 127.0.0.1:<random port>, password-protected
Kiwix JS / GPXSee — separate viewer programs started on request
```

## Startup

1. The launcher resolves the CacheNorth root from its own location (drive-letter and path independent) and allows one instance per root.
2. It starts the backend with `--headless --root <root> --session-file <file> --parent-pid <pid>`.
3. The backend binds a random loopback port, creates a random session token, and writes the dashboard URL to the session file.
4. The launcher opens the URL (token in the fragment, never sent to the server) in WebView2, or in the default browser if WebView2 is unavailable.
5. The backend detects CPU features with KoboldCpp's bundled probe, chooses the model, context size, and acceleration for this computer, and starts KoboldCpp.

## AI engine (engine.py)

- **CPU flags:** AVX2 → default backend; AVX only → `--noavx2`; neither → `--failsafe`.
- **GPU:** one Vulkan attempt, classified on failure (Windows security block, missing driver, stalled library load, timeout). KoboldCpp inherits a "no error dialogs" mode so a blocked library fails fast. A 60-second watchdog abandons a stalled load.
- **Context:** the planner (`context.py`) estimates memory from GGUF metadata. If the chosen size fails after model loading began, the engine retries once with a smaller safe size.
- **Lifetime:** KoboldCpp runs in a kill-on-close Job Object, so it cannot outlive the backend. Shutdown stops it, waits, closes logs, and removes the session file.

## Requests

- Every `/api/` call needs the `X-SWS-Token` header. Non-loopback `Host` and cross-origin `Origin` headers are rejected. Responses carry a strict Content-Security-Policy.
- Chat: `prompting.build_messages()` fits the system prompt, the current question, any document passages (inside the single system message, marked untrusted), and as much recent history as fits. The result streams back as NDJSON.
- Document search uses SQLite FTS5 with BM25 ranking and an overlap filter. Source cards are exactly the passages sent to the model.

## Shutdown

**Close CacheNorth** in the dashboard or the window's X: the backend stops generation and KoboldCpp, closes the server, and deletes the session file; the launcher waits for it and exits. If the launcher dies, the backend notices the missing parent process and shuts down.

## Portability assumptions

- Everything is relative to the root folder. No registry writes, no installation, no fixed drive letters or user names.
- Needs: 64-bit Windows 10/11, a writable root folder, writable `%TEMP%` with 512 MB free (checked before starting the engine), and loopback networking allowed by security software.
- The per-computer identifier is a hash of Windows' `MachineGuid`. Re-imaging a PC counts as a new computer.
- Not yet verified: Windows 10, ARM64 Windows (unsupported: x64 binaries only), locked-down corporate PCs (App Control may block unsigned files), and non-English Windows.
