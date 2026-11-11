# CacheNorth source handoff requirements

This document is a staging requirement, not a declaration that CacheNorth is ready to publish. The private repository's release gate is tracked in [issue #2](https://github.com/securitywithsam/CacheNorth/issues/2).

## Input

Use the latest **verified v1.0.3** development source at the owner's private development workspace. Inspect the latest Claude changes and test reports before exporting. Never export a copied USB installation as the canonical source.

## Deliver a source-only export

- Include original Python, JavaScript, HTML/CSS, C#/launcher projects, test fixtures that contain no user data, packaging definitions, dependency lists, reproducible build scripts, and required first-party assets.
- Add accurate instructions for clean Windows installation, development, tests, packaging, optional KoboldCpp setup, and obtaining **separately licensed** models and offline content.
- Pin dependency versions and provide upstream URLs and known hashes where appropriate. Document which steps require internet and which can work offline.
- State what is supported, what was tested, and what remains unverified. Do not claim full Windows 10/Intel/8 GiB acceptance without real evidence.
- Keep the current application branding if owned by Security With Sam. Do not embed local filesystem paths or the developer's name/email in example output.

## Exclude from the export

- GGUF models, ZIM archives, map tiles/MBTiles, third-party executables and DLLs whose redistribution has not been cleared.
- USB image contents, backups, `build/`, `release/` binaries, generated EXEs, large test acceptance copies, Python caches, caches and `_MEI*` directories.
- Runtime settings, logs, model selections, session files, browser profiles, local indexes, document libraries, private conversations, user-provided PDFs, personally identifying files, tokens, passwords and environment secrets.
- Any file not required to build, test or document the application, unless there is a specific, documented reason.

## Review gates

1. Inventory every exported file with relative path, size, SHA-256 and origin.
2. Inspect all exported files, hidden files and archives for credentials/private data before creating a ZIP. A `.gitignore` alone cannot protect already tracked or packaged data.
3. Check author information and history if exporting from a Git repository. Prefer a fresh source-only export rather than importing unreviewed development history.
4. Inventory licenses and copyright/provenance for included third-party code and assets. Do not invent a license for original code or imply third-party redistribution permission.
5. Build and test from a clean extracted export, not from the original working directory; report failures honestly.
6. Create a SHA-256 manifest, dependency/license report and handoff summary with any remaining blockers.
7. Stop before pushing to GitHub, publishing Releases, changing repository visibility or writing to the USB.

## Recommended export destination

`output/github-export/CacheNorth-v1.0.3-source-only.zip`

Also supply `GITHUB_HANDOFF.md` and `SHA256SUMS.txt` alongside the archive. Share the final ZIP here for review and import through a separate private GitHub pull request.
