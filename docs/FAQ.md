# Frequently asked questions

### Does CacheNorth need internet?

The main app, bundled AI models, knowledge archives, maps, and guides work locally once the ZIP is downloaded and extracted. Some third-party viewers may check for updates when your computer is online.

### Is this the same as downloading GitHub's source ZIP?

No. Use the [Full Portable ZIP](../README.md#download) to run CacheNorth. **Code → Download ZIP** is for developers and does not include the curated models and offline libraries.

### Do I need a GPU?

No. **CPU** is the default. Optional Vulkan GPU acceleration is experimental and can fall back to CPU if a GPU route is unavailable or blocked.

### Which AI model should I use?

Start with **Automatic**. It normally picks **Qwen3 1.7B** on systems with less than 12 GB RAM and **Qwen3.5 4B** on systems with more memory. The package also includes Qwen3 4B.

### Can I add any GGUF?

CacheNorth currently recognizes Qwen-family architectures with a chat template. Another model family can show **unsupported**.

### What are GGUF and ZIM?

**GGUF** is a file format for locally running AI models. **ZIM** is a compressed offline website/archive format used by Kiwix.

### Where are my chats and documents stored?

On the CacheNorth drive under its data folders. They are **not encrypted** by CacheNorth. Protect sensitive USB drives, and avoid uploading personal data in support reports.

### Can I use a different USB drive letter?

Yes. CacheNorth discovers its files relative to the launcher. Move the entire folder and keep its internal structure.

### What if Windows blocks an executable?

The executables are unsigned. Verify the official download and its SHA-256, understand the risk, and follow your device's security policy. Do not disable security protections. If an optional GPU library is blocked, CacheNorth can fall back to CPU.

### Can I sell or redistribute CacheNorth?

Original CacheNorth code uses a [proprietary early-access license](../LICENSE), while bundled software and content have separate rights. iFixit's noncommercial restriction and some Chromium/Electron corresponding-source obligations remain unresolved. Review the [license register](legal/THIRD_PARTY_LICENSES.md) before any redistribution.

### Where do I get help?

Start with [Getting Started](GETTING_STARTED.md), [Add Your Content](ADD_YOUR_CONTENT.md), and [Troubleshooting](TROUBLESHOOTING.md). Report a reproducible issue using the GitHub issue form without personal data.
