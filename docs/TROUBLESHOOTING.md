> **v1.0.3.1 packaging update (November 2026):** A separately cleaned and tested portable package is being prepared. It has 2,933 files (17,300,263,255 uncompressed bytes), refreshed beginner PDFs, three verified Qwen GGUFs, five ZIM archives, four maps, five content guides, source and attribution materials, and no retained chat/browser/log data. The original v1.0.3 [download](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3-Full-Portable.zip) and its [checksum](../SHA256SUMS.txt) remain historical and unchanged. **The v1.0.3.1 download URL, compressed size and SHA-256 are pending the owner's upload; do not substitute the old checksum.** See [package changes and open issues](V1031_RELEASE_CANDIDATE.md). The repo remains private.

# CacheNorth Troubleshooting

## CacheNorth does not open

Open the portable drive in File Explorer and run `Launch CacheNorth.exe` from the drive root. Keep the `Apps` folder beside the launcher. If Windows shows a SmartScreen warning, verify that the file came from Security With Sam, check the official download source and SHA-256 (the app is unsigned), and follow your organization's security policy. Never disable Defender or SmartScreen.

## A model shows unsupported or too large

CacheNorth currently supports **Qwen-family GGUF** models only. An unsupported label may mean a different model architecture; choose one of the bundled Qwen models or check the source/model format. A too-large label means the model may exceed available system memory: choose Qwen3 1.7B, close memory-intensive programs, or use a machine with more RAM. Use **AI Model Manager** and **Refresh All** after adding a model.

## The AI engine does not start

Open `Apps\Offline AI\Data\Logs\koboldcpp.log`. Confirm that `Apps\Offline AI\KoboldCpp\koboldcpp-launcher.exe` and the Qwen GGUF model remain in their original relative locations. Check available RAM and Windows temporary storage. CacheNorth performs its allowed attempt and reports failure without entering a restart loop. The unpacked runtime runs in place and avoids per-launch PyInstaller extraction into Windows temporary storage. Keep every file in the KoboldCpp folder together; missing CPU or Vulkan DLLs can force fallback or prevent startup.

## Choosing a context length

Settings > Context length controls how much conversation and document text the AI can consider at once. Automatic (recommended) picks 2K, 4K, or 8K tokens from installed RAM, then lowers the size if the current model would not fit comfortably in available memory. You can choose 2K, 4K, 8K, 16K, or 32K instead. The choice is saved for this computer only, and options larger than the model supports are disabled.

Each option shows estimated system memory and, in GPU mode, graphics memory for the current model. Conversation memory is calculated exactly from the model file; other memory is a conservative estimate measured with KoboldCpp 1.124.2. An option marked "may exceed memory" needs confirmation. If a size cannot start, CacheNorth retries once with a smaller safe size, reports it in Settings and System Status, and uses the safe size on that computer until the setting is applied again.

Larger contexts do not make answers faster or smarter. A long conversation must be read in full before the first word appears, which can take minutes on an older CPU. The full conversation always stays saved; when it does not fit, the oldest messages are left out of what is sent to the AI, and a notice says how many.

## The computer has limited memory

Systems reporting less than 10 GiB use a 2,048-token context. Close other applications before loading the model. Physical 8 GiB acceptance remains pending, so v1.0.3.1 has not been physically acceptance-tested on an 8 GiB computer.

## GPU acceleration is unavailable

Choose CPU under Settings, AI acceleration and apply the change. CPU mode is the compatibility baseline and requires no NVIDIA GPU, CUDA installation, or dedicated graphics card. Automatic GPU and Manual GPU make one startup attempt and fall back to CPU if the selected path fails.

GPU choices are saved separately for each computer. Plugging the drive into another computer starts in CPU mode until GPU is chosen on that computer. After a failed GPU attempt, CacheNorth pauses GPU on that computer and starts in CPU mode. To try again, choose a GPU mode in Settings and select Apply and restart AI. Settings shows the selected mode, the mode actually running, the graphics device, how many model layers are on the GPU, and the reason for any fallback. GPU is reported only when the AI engine confirms layers were offloaded.

## Windows blocked a KoboldCpp GPU component

On Windows 11, Smart App Control or an organization's App Control policy can block `koboldcpp_backend.dll` in `Apps\Offline AI\KoboldCpp\backend_routes\koboldcpp_vulkan`. You may see "koboldcpp-launcher.exe - Bad Image" with error `0xc0e90002`, or a Windows Security notice saying part of KoboldCpp was blocked because its publisher could not be confirmed. The KoboldCpp GPU components are open-source files that are not digitally signed. CacheNorth's copies match the official KoboldCpp 1.124.2 release byte for byte, but Windows can still refuse unsigned files.

This is a Windows security decision, not a hardware fault. CacheNorth never disables or bypasses Smart App Control, Microsoft Defender, or App Control policies, and does not add exclusions. When Windows blocks the GPU component, CacheNorth stops the attempt, starts CPU mode, records the reason, and does not try GPU again on that computer until you ask it to. Automatic GPU is skipped while Smart App Control is on unless GPU has already worked on that computer; Manual GPU can still be tried once. CPU mode remains fully usable.

To check the reason, look in `Apps\Offline AI\Data\Logs\koboldcpp.log` for `WinError 4551` ("An Application Control policy has blocked this file"). Windows also records the block in Windows Security > Protection history and in Event Viewer under Applications and Services Logs > Microsoft > Windows > CodeIntegrity > Operational.

## The CPU is old or unsupported

CacheNorth uses its bundled CPU probe to select AVX2 CPU mode, AVX1 `--noavx2`, or KoboldCpp `--failsafe`. Failsafe is intentionally slow and reserved for x64 processors without AVX. If the process exits, record the CPU model and log; that physical CPU remains unverified until tested.

## Temporary storage is full or restricted

CacheNorth requires at least 512 MiB of writable Windows temporary storage before model launch. Free space in the current user's temporary folder or ask the computer owner to correct its permissions.

## A document cannot be indexed

Supported formats are PDF, TXT, and Markdown, up to 250 MiB. Image-only PDFs need OCR before their text can be searched. Malformed or encrypted documents may be rejected. Keep an original backup and treat imported files as untrusted.

## Kiwix does not open an archive

Choose Knowledge Library and use **Open in Kiwix** beside the desired archive. If the archive does not appear, confirm that its `.zim` file remains directly inside `Library`. Kiwix is an independent third-party viewer and can keep its own local preferences.

## A map does not open

Choose Offline Maps and select **Open map**. Confirm that the file remains directly inside `Maps` and that `Apps\GPXSee\GPXSee.exe` exists. These maps provide offline viewing, not live traffic, current closures, GPS guidance, or turn-by-turn navigation.

## The drive letter changed

Open the new drive letter and run `Launch CacheNorth.exe` again. All product paths derive from the launcher location. Shortcuts pointing to an old drive letter may need recreation.

## The portable drive is read-only

Chat history, imported documents, indexes, settings, and logs require writable portable storage. Remove physical write protection or copy the complete kit to writable media. CacheNorth reports this condition during startup.

## Safe shutdown

Stop any generation, close opened documents, Kiwix, and GPXSee, select **Close CacheNorth**, wait for drive activity to finish, and use Windows Safely Remove Hardware.

CacheNorth waits for the AI engine to exit, removes its session file, flushes logs, and then releases its final Windows Job Object safeguard. If shutdown exceeds the bounded wait, record the current log and use Task Manager to confirm whether a CacheNorth or KoboldCpp process remains before removing the drive.

## Privacy and traces

CacheNorth directs its application data to the portable data folder and binds its local services to loopback. Windows, browsers, Defender, Kiwix, GPXSee, and opened documents can create temporary files, caches, recent-file records, compatibility records, or registry settings. CacheNorth makes no zero-trace claim.
