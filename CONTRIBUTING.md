# Contributing to CacheNorth

Thanks for helping improve portable offline computing.

## Current project status and permissions

CacheNorth's **original code is proprietary** under [LICENSE](LICENSE). Viewing source and running an official unmodified build for personal, noncommercial evaluation does **not** automatically authorize redistribution or publication of modified builds.

You are welcome to report issues, suggest features, and provide feedback. **Ask the maintainer before submitting a source-code contribution or publishing a fork.** The maintainer can discuss permission for a specific contribution. Do not assume the repo is open source.

If a contribution is accepted, the contributor must have the rights to submit it and agree on its incorporation into CacheNorth, including any future commercial edition. Such terms must be agreed in writing before merging substantial outside code. Third-party material retains its own licenses, and these instructions do not limit rights granted by those licensors.

## Before reporting an issue

1. Check for an existing report about the problem.
2. Include CacheNorth version (for example v1.0.3), Windows build, CPU/RAM/GPU, AI model, acceleration mode, expected and observed results, and reproduction steps.
3. Say whether the problem occurs in the **hosted portable ZIP** or a **source build**; these may differ.
4. Remove usernames, local paths, chats, documents, session URLs, tokens, passwords, cookies, and browser-profile data from logs and screenshots. Do not upload the entire USB or browser profile.

Use [Security](SECURITY.md) for private reporting of vulnerabilities.

## Development and testing guidance (for authorized contributors)

- Coordinate scope before modifying application source.
- Keep personal USB drives and third-party content out of tests; use temporary fixtures.
- Preserve drive-letter independence and paths containing spaces.
- Add regression tests and record Windows behavior when practical.
- Test the packaged application separately from Python source; passing CI does not prove full-ZIP compatibility.
- Never commit model weights, ZIMs, maps, binaries, personal data, or content without approved redistribution rights.
- See [Building](docs/BUILDING.md), [Release readiness](docs/FULL_PORTABLE_RELEASE_CHECKLIST.md), and [Source vs. Hosted ZIP](docs/SOURCE_VS_HOSTED_ZIP.md).

**The GitHub repository is private during early-access preparation.** Release and visibility decisions belong to the maintainer.
