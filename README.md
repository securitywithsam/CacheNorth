# CacheNorth

**Your knowledge. Anywhere.**

CacheNorth is an offline-first, portable Windows toolkit by **Security With Sam**. It brings local AI chat, document search, offline reference libraries, maps, and practical guides together in one interface that can run from a USB drive.

> **Release status:** Public source and downloads are being prepared. This repository documentation is a draft until the final compatibility, security, and third-party rights checks pass. There is no public installer or complete USB image available from this page yet.

## What CacheNorth does

- **Local AI chat:** Run compatible GGUF models through KoboldCpp without sending prompts to a hosted AI provider.
- **Ask Documents:** Search locally indexed documents and retrieve source-backed answers with citations.
- **Offline knowledge:** Discover compatible Kiwix ZIM archives stored on the drive.
- **Offline maps:** Open map resources using a compatible map viewer.
- **Guides:** Browse locally stored PDF help and reference material.
- **Portable dashboard:** A Windows launcher and WebView2 interface with a browser fallback.
- **Hardware-aware options:** CPU inference, optional Vulkan acceleration, model selection, and configurable context length where supported.

CacheNorth is designed to work without an internet connection. Some separately bundled third-party programs or Windows components may use network services when online; those behaviors are being reviewed and documented before public release.

## Platform and requirements

- **Primary target:** Windows 11, x64.
- **Other environments:** Windows 10, older CPUs, lower-memory systems, and different GPUs require additional physical acceptance testing.
- **Models and content:** Users will need to provide compatible models and knowledge resources from sources whose terms allow their intended use.
- **Storage:** Depends heavily on the selected models, maps, and offline archives.

## Project structure

The planned public source layout separates original application code from external content:

| Folder | Purpose |
| --- | --- |
| `src/` | Python application and services |
| `dashboard/` | Local web interface |
| `launcher/` | Native Windows launcher |
| `scripts/` | Build, verification, and maintenance scripts |
| `tests/` | Automated regression tests |
| `docs/` | Architecture, setup, troubleshooting, and compatibility notes |
| `.github/` | Community templates and automation |

These folders will be populated from the final reviewed source tree. Large GGUF/ZIM/map files, personal data, and development builds should not be committed to Git history.

## Build and setup

Reproducible build instructions and verified dependency versions will be published after the final application candidate passes review. For now, please do not treat the development USB contents as an approved redistribution package.

## Privacy and safety

- The local inference API is intended to bind to the local computer.
- Conversations and imported documents stored on removable media may be readable by anyone who obtains that drive unless it is encrypted.
- AI-generated information can be inaccurate. Verify important technical, medical, emergency, and safety information against trusted sources.
- Respect Windows application-control decisions; CPU inference should remain available when optional GPU libraries are blocked.

## License and third-party components

**The CacheNorth project's own license has not yet been selected.** Repository visibility alone does not grant reuse rights. Third-party applications and content have separate licenses and attribution requirements. See [`docs/SUPPLY_CHAIN_AND_LICENSE_REVIEW.md`](docs/SUPPLY_CHAIN_AND_LICENSE_REVIEW.md) before distributing any binary or data bundle.

## Contributing and support

Community contribution guidance is in [`CONTRIBUTING.md`](CONTRIBUTING.md). Please use GitHub Issues for reproducible bugs and feature requests once the public repository opens. For security concerns, follow [`SECURITY.md`](SECURITY.md).

Created by **Security With Sam**.
