> Historical planning document archived November 2026. For the current package consult [v1.0.3.1 release notes](../V1031_RELEASE_CANDIDATE.md) and [current release checklist](../FULL_PORTABLE_RELEASE_CHECKLIST.md).

# CacheNorth public-release gate

This checklist is for the source repository **and** any downloadable package. An earlier successful USB deployment is personal-test acceptance, not a public redistribution clearance.

## Before publishing a repository

- [ ] Confirm the GitHub account and final repository name; create the repository **private first**.
- [ ] Remove internal preparation and handoff notes (including `docs/CLAUDE_HANDOFF.md` and `REVIEW_BEFORE_PUBLISHING.md`) from the public tree.
- [ ] Obtain the final Claude/Codex source tree; identify the exact commit and release version.
- [ ] Review current `git status`, tracked files, full history, and hidden paths for personal files and credentials.
- [ ] Run a secrets scan on the complete repository history before making it public.
- [ ] Remove username/drive-specific paths from build instructions and specs, or parameterize them.
- [ ] Confirm `.gitignore` excludes all private data, models, maps, archives, generated binaries, temp backups, and USB images.
- [ ] Inspect logos and screenshots for redistribution permission and personal details.
- [ ] Select and review the license for **original CacheNorth code**. Do not infer a license from included GPL/AGPL tools.
- [ ] Keep third-party licensed code distinctly identified, with correct notices and corresponding source where needed.
- [ ] Document reproducible build steps, pinned dependencies, and supported Windows versions.
- [ ] Add CI only after the actual test/build commands and dependencies are verified.
- [ ] Verify README claims against the final packaged candidate; avoid untested claims about all PCs or fully network-silent behavior.
- [ ] Publish only after a final review of the complete contents and history.

## Before attaching a downloadable Windows package

- [ ] Resolve GPL/AGPL/LGPL compliance for every redistributed third-party executable/library, including source obligations.
- [ ] Verify provenance, redistribution terms, version, and SHA-256 for every model.
- [ ] Verify per-archive and per-map rights and attribution, including third-party embedded images.
- [ ] Exclude content without proven redistribution rights, even from a free download.
- [ ] Include third-party notices, source links/offers as required, and OpenStreetMap attribution where applicable.
- [ ] Confirm appropriate handling of unsigned executables and Windows App Control without requiring users to disable protection.
- [ ] Build from a clean tree, validate release hashes, and perform physical acceptance on hardware beyond the development PC.
- [ ] Verify clean initial `Data` with no chats, documents, indexes, tokens, browser profiles, or test logs.
- [ ] Verify successful cold-start, fallback, offline usage, and shutdown; no temp or managed-process leaks.
- [ ] Publish release notes, SHA-256 checksums, system requirements, and honest limitations.

## GitHub size strategy

Keep source and documentation in ordinary Git. Do not commit multi-GB model and archive files or a complete USB/VHDX image. Once rights are cleared, distribute approved standalone archives through release assets or documented upstream downloads, subject to the current per-asset limits.
