# Configuring and customizing CacheNorth

## Settings page

| Setting | Options | Saved |
|---|---|---|
| AI model | Automatic (recommended) or a specific model | For the drive |
| AI acceleration | CPU (default), Automatic GPU (experimental), Manual GPU (advanced) | Per computer |
| Context length | Automatic (recommended), 2K, 4K, 8K, 16K, 32K tokens | Per computer |

"Per computer" means the choice is stored under an anonymized identifier for that Windows installation (a one-way hash, not the raw machine ID). Taking the drive to another PC starts with CPU and Automatic context there.

### CPU and GPU

- **CPU** works everywhere. CacheNorth detects AVX2, AVX, or neither and starts the matching KoboldCpp backend.
- **Automatic GPU** tries Vulkan on the best available device. **Manual GPU** lets you pick a device. Device numbers are confirmed after the first successful GPU start.
- If a GPU start fails, CacheNorth starts CPU mode once, shows the reason, and pauses GPU on that computer until you apply a GPU mode again. It never retries in a loop.
- GPU is reported only when the engine confirms model layers were offloaded.
- With **Windows Smart App Control** on, Windows may block KoboldCpp's unsigned GPU files. Automatic GPU is then skipped, Manual GPU is tried once, and CPU mode is unaffected. CacheNorth never changes Windows security settings.

### Context length

How much conversation and document text the AI can consider at once. Each option shows estimated system memory (and graphics memory in GPU mode) for the current model; options that may exceed available memory need confirmation. Larger contexts are slower on CPUs because the whole prompt is read before the first word appears. A size that cannot start falls back once to a safe size and is remembered for that computer. The full conversation is always saved, even when older messages do not fit and are left out of what is sent.

## Where data is stored

Everything lives under `Apps\Offline AI\Data` on the drive:

| Path | Contents |
|---|---|
| `settings.json` | Model choice and per-computer GPU and context settings |
| `model-compatibility.json` | Which models have loaded successfully on which computer (anonymized) |
| `Chats\chats.sqlite3` | Saved conversations (unencrypted) |
| `Documents\`, `Index\documents.sqlite3` | Your added documents and their search index |
| `Logs\koboldcpp.log`, `Logs\launcher.log` | Engine and launcher logs (no conversation text; session tokens are redacted) |
| `WebView2\` | The built-in window's browser profile |
| `GPXSee\` | Map viewer settings |

To reset CacheNorth, close it and delete `settings.json`. To remove all conversations, use **Settings > Clear saved conversations**. Deleted data may remain recoverable on flash media; use an encrypted drive if that matters.

## Customizing the source

| To change | Edit |
|---|---|
| Assistant instructions (system prompts) | `GENERAL_SYSTEM_PROMPT` and `DOCUMENT_SYSTEM_PROMPT` in `src/security_with_sam/app.py` |
| Sampling (temperature, top-p, output limits) | `stream_chat()` in `src/security_with_sam/engine.py`; `max_output_for()` in `context.py` |
| Context options and memory estimates | `OPTIONS` and the overhead constants in `src/security_with_sam/context.py` |
| Supported model architectures | `supported = architecture in {...}` in `src/security_with_sam/models.py` (KoboldCpp must also support the architecture) |
| Automatic model choice | `ModelManager.automatic()` in `models.py` |
| Archive titles and categories | `_archive_title()` and `_archive_category()` in `src/security_with_sam/integrations.py` |
| Map file types | `allowed` in `Integrations.map_files()` |
| Dashboard text, layout, colors | `dashboard/index.html`, `dashboard/styles.css` (color variables at the top), `dashboard/app.js` |
| Branding | `dashboard/cache-north-logo.png`, `dashboard/favicon.ico`, `launcher/CacheNorth.ico`, window title in `launcher/StartOfflineAI.cs` |
| KoboldCpp version | `third_party/manifest.json` (URL, SHA-256, unpacked tree hash), then rerun `fetch_third_party.ps1` |

After changes, run `scripts\test.ps1` and rebuild. If you redistribute a modified build, follow the third-party obligations in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) and do not present it as an official Security With Sam release.
