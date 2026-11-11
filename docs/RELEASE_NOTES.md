# CacheNorth Release Notes

## v1.0.3.1 — cleaned portable package (pending upload)

Packaging/documentation update; application binaries and behavior unchanged. The maintainer reports 2,933 files, 17,300,263,255 bytes uncompressed; three validated Qwen models, five ZIMs, four maps, five guides; regenerated beginner PDFs; privacy cleanup; refreshed GPL/AGPL/LGPL source and attribution materials. All 19 functional tests on one Windows 11 PC passed, including CPU chat, documents, Kiwix, maps, guides, shutdown and alternate drive letter. Windows 10, 8 GB RAM, GPU and downloaded-ZIP SmartScreen acceptance remain untested. Rights/source-distribution review of Chromium/Electron and noncommercial iFixit content remains open. The original v1.0.3 download and checksum remain unchanged. Owner reports the cleaned archive as [CacheNorth-v1.0.3.1-Full-Portable.zip](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip), compressed length 15,993,029,771 bytes, SHA-256 `4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED`; the hosted copy still needs independent verification. See [candidate notes](V1031_RELEASE_CANDIDATE.md).


## Source distribution of 1.0.3 (2026-11)

The application code is unchanged from the 1.0.3 build deployed for personal testing. This release prepares the source for GitHub:

- Reproducible build: `scripts/bootstrap.ps1`, a new `scripts/fetch_third_party.ps1` (official downloads, SHA-256 verified, KoboldCpp unpack verified by a whole-tree hash), and a portable `scripts/build.ps1` that writes to `dist\` and never overwrites without `-Force`.
- Exact dependency pins in `requirements/`. `cryptography` is now an explicit runtime dependency (it was previously bundled only because it happened to be installed).
- Public documentation (installation, building, configuration, architecture, third-party licenses, security) and a proposed GitHub Actions workflow.
- Acceptance scripts now refuse removable drives unless `--allow-removable` is passed, instead of assuming one drive letter.

## Version 1.0.3 - per-computer context length

- Added Settings > Context length: Automatic (recommended), 2K, 4K, 8K, 16K, and 32K tokens. Choices are saved per computer, like GPU settings, and are capped at the maximum the model declares (40,960 for Qwen3, 262,144 for Qwen3.5).
- Each option shows estimated system and graphics memory for the selected model and acceleration mode. KV-cache size is calculated from GGUF metadata and matched KoboldCpp 1.124.2's own allocation to the MiB in all 30 measured runs (3 models x 5 sizes x CPU/Vulkan). Total-memory allowances were fitted to measured commit charge and kept conservative.
- Options estimated to exceed available memory require explicit confirmation before they are applied.
- Automatic keeps the previous RAM tiers (2K/4K/8K) and steps down when the model would not fit comfortably in available memory or graphics memory.
- A context size that fails to start is retried once with a smaller safe size, reported in Settings and System Status, and remembered for that computer. A GPU start blocked by Windows security or a missing driver is not retried with a smaller context, so the Windows prompt is not repeated.
- Chat requests now fit the running context. The system prompt and current question are always sent unchanged; a question too long for the context is refused with a clear message instead of being truncated. Document passages and history are added within the remaining budget, using the model's own tokenizer when available. The full conversation stays saved, and a notice reports how many older messages were not sent.
- Document passages now sit inside the single system message as untrusted data (some chat templates reject a second system message). Source cards show exactly the passages sent.
- Fixed a server error when an Ask Documents question contained only common words.
- System Status shows the requested and actual running context sizes.

## Version 1.0.2 - Windows security compatibility and CPU-first GPU handling (candidate)

- Field issue: on a Windows 11 laptop (build 26200), Smart App Control blocked the unsigned KoboldCpp Vulkan route library `backend_routes\koboldcpp_vulkan\koboldcpp_backend.dll` (`WinError 4551` / `0xc0e90002`). The deployed file matches a fresh unpack of the official KoboldCpp 1.124.2 release, whose published SHA-256 also matches.
- The GPU choice had been stored once on the drive, so Automatic GPU chosen on the development desktop was applied on the laptop. GPU choices, failures, and verified Vulkan devices are now stored per computer under an anonymized identifier, and every new computer starts in CPU mode. The legacy shared setting is ignored and reset to CPU.
- A failed GPU attempt is remembered for that computer; later startups and model switches use CPU without re-triggering Windows security prompts until the user applies a GPU mode again.
- Automatic GPU is skipped while Smart App Control is on unless GPU already worked on that computer. Manual GPU can still be tried once. Smart App Control state is read only and never changed.
- GPU failures are classified as Windows security block, library-load stall, missing Vulkan device or driver, timeout, or other failure, with a plain-language reason in Settings.
- KoboldCpp now inherits a quiet process error mode, so a blocked library returns an error instead of waiting behind a modal loader dialog. A 60-second watchdog also abandons a GPU attempt stuck at library load, and the Job Object cleans up the process.
- Settings and System Status now report the selected mode, the mode actually running, the Vulkan device, and verified offloaded layers. GPU is never reported when zero layers are offloaded.
- Regression suite: 82 Python tests (15 new) and 3 dashboard keyboard tests.

## Version 1.0.1 - performance, reliability, GPU controls, and shutdown hotfix

- Fixed a packaged-runtime CPU detection failure that forced KoboldCpp 1.124.2 into `koboldcpp_failsafe.dll` on an AVX2 Ryzen 7 7800X3D. The release now includes the official 32 KiB KoboldCpp CPU probe, passes explicit AVX2/AVX1/failsafe flags, and uses seven physical-core-oriented threads on the development host.
- Improved repeated CPU generation from approximately 2.6-3.1 tokens/s in deployed failsafe logs to 16.7-19.7 tokens/s for Qwen3 4B, 34.3-46.5 tokens/s for Qwen3 1.7B, and 13.5-16.9 tokens/s for Qwen3.5 4B on the development computer.
- Added exact latest-response prompt and generation telemetry, a single-generation lock, bounded request timeouts, empty-output errors, and stale-metric clearing after model changes.
- Corrected the inherited `Qwen3 4B Instruct AWQ` label to `Qwen3 4B Instruct (GGUF Q4_K_M)`; the installed file is valid GGUF Q4_K_M.
- Added CPU, automatic Vulkan, and manual Vulkan-device controls with physical NVIDIA/AMD/Intel adapter filtering, tracked restart progress, one CPU fallback, and CPU as the default.
- Made dashboard shutdown close the native WebView2 host automatically. Backend exit also closes the launcher as a bounded fallback; ready-state native shutdown leaves zero managed processes and removes the session file.
- Updated all three customer guides, runtime metadata, release reporting, and deployment tooling for v1.0.1.
- Added the official KoboldCpp 1.124.2 unpacked portable runtime as the preferred execution layout while retaining the prior one-file executable as a fallback.
- Corrected shutdown ordering so the direct KoboldCpp process is stopped and awaited before the kill-on-close Job Object is released as the final process-tree safeguard, and added an explicit completion barrier so the packaged controller waits for process cleanup, log closure, and session-file removal.
- Forced failure of every packaged Vulkan backend variant now proves automatic CPU recovery. Shutdown during a real active generation stream also completes with zero managed processes and a removed session file.
- Final regression result: 67 Python tests and 3 dashboard keyboard tests passed. Corrected packaged CPU generation, three-model switching, document citations, Refresh All, automatic/manual Vulkan generation, forced CPU fallback, conversation persistence, both native shutdown methods, and zero new extraction-directory growth passed.

## Version 1.0.0 - audited deployment candidate

- Completed the CacheNorth by Security With Sam rebrand, official logo integration, native launcher icon, Windows metadata, loading screen, and six-section dashboard.
- Kept CPU-only inference as the compatibility baseline, with AVX2, AVX1 `--noavx2`, and x64 `--failsafe` selection.
- Kept optional Vulkan acceleration with one guarded CPU fallback and no automatic restart loop.
- Added conservative 2,048 / 4,096 / 8,192-token memory profiles for the 8 / 16 / 32+ GiB tiers.
- Added local SQLite FTS5 document retrieval, accurate PDF page citations, duplicate-content reuse, scanned-document guidance, removal, and index rebuild.
- Added direct archive selection for Kiwix and direct map selection for portable GPXSee.
- Added conversation history loading and deletion, clearer progress, actionable errors, and safe shutdown controls.
- Hardened Origin checking and retained loopback host enforcement, random session-token authorization, security headers, confined paths, safe subprocess argument lists, and job-object cleanup.
- Updated Flask to 3.1.3 and pypdf to 6.21.4 after dependency auditing. The post-update audit reported no known vulnerabilities in installed third-party Python packages.
- Added three redesigned CacheNorth guides, runtime license collection, a detailed licensing audit, and a collision-checked deployment manifest.
- Added the branded single-window WebView2 shell with automatic browser fallback and no silent runtime installation.
- Added dynamic Refresh Documents, Refresh Library, and Refresh Maps workflows.
- Corrected USB versus development storage identity and simplified System Status.
- Added working offline help buttons and fixed Enter-to-send while preserving Shift+Enter.
- Tightened retrieval relevance to remove generic and weak incidental citation cards.
- Final regression result: 53 Python tests and 3 dashboard keyboard tests passed; the CPU-model evaluation passed 8/8 checks.

## Acceptance boundaries

- Actual physical testing covers the Windows 11 development host, CPU inference, NVIDIA Vulkan, AMD integrated Vulkan, document retrieval, packaged relocation, and portable GPXSee.
- Windows 10, physical 8 GiB and 16 GiB systems, older physical CPUs, missing-driver hardware, and restricted enterprise environments still require independent acceptance testing.
- Commercial redistribution remains blocked by unresolved rights for the iFixit and MedlinePlus ZIM archives, archive-level review for Ready.gov, and proof of the exact offline map download provider.
