# Getting started with CacheNorth

CacheNorth is a Windows application that combines a local AI assistant, document search, and optional offline reference material. **There is currently no official prebuilt download.** This source preview must be built before use.

## Which setup should I follow?

| If you… | Start here |
|---|---|
| Want to see how CacheNorth works | Read [Features in README](../README.md#what-it-does) |
| Have a Windows PC and want to make your own USB | Follow the [build guide](BUILDING.md), then the [USB installation guide](INSTALLATION.md) |
| Already built CacheNorth and only need an AI model | Jump to [Add an AI model](INSTALLATION.md#3-add-an-ai-model) |
| Want Wikipedia, maps, or offline reference files | See [Content sources](CONTENT_SOURCES.md) |
| Hit a Windows warning or a model issue | See [Troubleshooting](TROUBLESHOOTING.md) |

## The shortest complete path

1. **Prepare a Windows 10/11 64-bit computer.** Windows 11 has been tested; Windows 10 needs real-world validation. You need PowerShell, the Windows .NET Framework C# compiler, and enough free space for build tools and models. See [prerequisites](BUILDING.md#prerequisites).
2. **Clone and build the source.** Run the four setup/test/build PowerShell commands in [Building](BUILDING.md#steps). The build downloads verified KoboldCpp and WebView2 SDK inputs; it does not contain AI model weights.
3. **Copy the resulting folder.** Put the contents of the generated dist/CacheNorth-1.0.3 folder on a writable USB drive, external SSD, or normal Windows folder. See [portable installation](INSTALLATION.md#2-copy-the-build).
4. **Add a model.** Download a compatible Q4_K_M GGUF model from a source listed in [Model downloads](CONTENT_SOURCES.md#ai-models-required). Copy it to the Models directory shown in the [installation guide](INSTALLATION.md#3-add-an-ai-model). A 1.7B model is the sensible place to start on lower-memory computers.
5. **Launch.** Double-click Launch CacheNorth.exe, wait for the engine to load, and try a short question in AI Chat. New computers start on CPU; GPU acceleration is optional.

That's enough to use offline AI chat. Add documents, ZIM archives, maps, or guides only if you want those features.

## What's included?

| Item | Included in source? | Where it comes from |
|---|---|---|
| CacheNorth application code and build scripts | Yes | This repository |
| Third-party AI runtime | Downloaded by the build script | [KoboldCpp](https://github.com/LostRuins/koboldcpp) |
| AI model weights | No | [Model links](CONTENT_SOURCES.md#ai-models-required) |
| Wikipedia and other offline encyclopedias | No | [Kiwix archives](CONTENT_SOURCES.md#offline-knowledge-optional) |
| Maps and viewer | No | [Maps](CONTENT_SOURCES.md#offline-maps-optional) |
| Your personal documents and guides | No | Add your own |

## Important limits

- The published source project is currently a **preview**, with no license for original CacheNorth code yet.
- Initial building and downloading need internet. Once installed, CacheNorth's AI and document features can operate locally.
- Conversations and documents are stored unencrypted on the portable drive. Encrypt the drive if loss or theft is a concern.
- Windows security settings can block unsigned acceleration components. CPU mode is the default; do not disable system protection just to use GPU mode.
- Results from local AI models are fallible. Verify critical medical, survival, or technical decisions.

**Next:** [Build from source](BUILDING.md) · [Portable installation](INSTALLATION.md) · [Troubleshooting](TROUBLESHOOTING.md)