# Security

## Reporting a vulnerability

Please report security problems privately to the maintainer through a secure channel. If GitHub private vulnerability reporting is enabled for this public repository, use **Security → Report a vulnerability**. Do not post sensitive security details in a public issue. Include the CacheNorth version, Windows version, and steps to reproduce. Do not include personal documents or conversations.

**Maintainer:** Confirm whether private vulnerability reporting is enabled and provide a private reporting channel if it is unavailable. This policy does not assert that the feature is enabled. If no private channel is available, open a public issue requesting one without disclosing vulnerability details.

## Security model

- **Local only.** The CacheNorth backend and KoboldCpp listen on `127.0.0.1` with random ports. Nothing is exposed to the network.
- **Session token.** Every API request needs a random per-session token (passed to the dashboard in the URL fragment, which browsers never send to servers). Requests with a non-loopback `Host` or a cross-origin `Origin` are rejected, and responses carry a restrictive Content-Security-Policy, `nosniff`, and frame denial.
- **KoboldCpp** gets a random per-session password and runs inside a Windows Job Object, so it cannot outlive CacheNorth.
- **Files.** Document, guide, archive, map, and model operations are confined to their folders with exact-name checks; uploads are limited to PDF/TXT/Markdown up to 250 MB. Subprocesses are started with argument lists, never a shell.
- **Untrusted documents.** Retrieved passages are marked as untrusted data inside the prompt, and the model is told to ignore instructions in them. This reduces but cannot eliminate prompt injection by a malicious document; the model has no tools and cannot run commands or reach files.
- **Native window.** WebView2 navigation is limited to the local dashboard; new windows, downloads, permission requests, context menus, and developer tools are blocked.
- **Build inputs.** Third-party binaries are downloaded from official sources and checked against SHA-256 values in `third_party/manifest.json`. A mismatch stops the build.
- **Windows security.** CacheNorth never disables or bypasses Microsoft Defender, Smart App Control, or App Control. If Windows blocks a component, CacheNorth falls back to CPU mode and reports it.

## Known limitations

- **Data at rest is not encrypted.** Conversations, documents, and indexes are stored in plain files on the drive. Use an encrypted drive (for example BitLocker To Go) if it could be lost. Clearing conversations deletes database rows but does not guarantee the data is unrecoverable from flash storage.
- **Executables are unsigned.** Windows SmartScreen or Smart App Control may warn about or block them; KoboldCpp's GPU libraries are also unsigned upstream.
- **Other local processes** running as the same Windows user can read CacheNorth's files, including the session file while it runs, and can see the KoboldCpp password on its command line. CacheNorth does not defend against malware already on the computer.
- **PDF parsing** runs inside the backend without a time limit. A deliberately malformed PDF could slow or stall indexing. Only add documents you trust.
- **Third-party components:**
  - KoboldCpp 1.124.2 embeds its own Python 3.8 and OpenSSL 1.1.1, both end-of-life upstream. This exposure is reduced because CacheNorth keeps KoboldCpp on loopback with a password.
  - The WebView2 runtime and Kiwix JS may contact Microsoft or GitHub services when the computer is online.
  - Keep dependencies updated in `requirements/` and `third_party/manifest.json`.
- **Model output can be wrong.** Verify medical, legal, navigation, electrical, and emergency information against authoritative sources.
