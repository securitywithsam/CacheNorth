# Getting started

You can run CacheNorth from a Windows folder or copy it to a USB drive. You don't need Python or developer tools for the **Full Portable ZIP**.

## 1. Download

Get [CacheNorth v1.0.3.1](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip). It is about 14.9 GiB, so the download may take time.

Make sure you have enough space for both the ZIP and the extracted application. The extracted folder is about 17.3 GB. A 32 GB or larger USB drive is recommended.

> [!TIP]
> The green GitHub **Code → Download ZIP** button downloads **developer source**, not the ready-to-run CacheNorth application.

## 2. Extract

In File Explorer, right-click the downloaded ZIP and choose **Extract All**. Use a writable folder or a USB drive formatted exFAT or NTFS.

Keep the entire `CacheNorth-v1.0.3.1-Full-Portable` folder together. You can move the folder between drive letters.

## 3. Launch

Open the extracted folder and double-click `Launch CacheNorth.exe`. The dashboard opens in its own window when WebView2 is available.

The executable is unsigned. Windows may warn or block it. Check that it came from the [official download](../README.md#download) and [verify the SHA-256](../README.md#download). Follow your device's security policy; never disable Windows protections to launch it.

First startup may take longer from a slow USB drive.

## 4. Start a chat

1. Open **AI Chat**.
2. Leave the model on **Automatic** for the first test.
3. Type a simple question and press **Enter**. Use **Shift+Enter** for a line break.
4. Wait for the AI to answer. CPU speed depends on your hardware.

Automatic normally chooses **Qwen3 1.7B** below 12 GB RAM and **Qwen3.5 4B** otherwise. All three bundled models are Qwen-family GGUF files. A GGUF is a local AI-model file.

## Explore the rest

| Dashboard section | What you can do |
|---|---|
| **Knowledge Library** | Open downloaded ZIM archives in Kiwix; a ZIM is an offline website/library file |
| **Document Search** | Add PDF, TXT or Markdown documents and ask questions with source cards |
| **Offline Maps** | Open Mapsforge maps in GPXSee |
| **Guides** | Open bundled reference PDFs |
| **Settings** | Change **AI Model Manager**, **AI acceleration**, **Context length**, and privacy/safety options |
| **System Status** | See information about the current session and storage |

Click **Refresh All** at the top right after adding models, maps, archives or guides.

## Add your own files

[Add Your Content](ADD_YOUR_CONTENT.md) has the exact folders and official starting-point links.

## First-run checklist

- [ ] The dashboard opens.
- [ ] **AI Chat** answers a question.
- [ ] **Knowledge Library** opens an archive.
- [ ] **Offline Maps** opens a regional map.
- [ ] **Guides** opens a PDF.
- [ ] Close CacheNorth and any external viewers before ejecting your USB.

Chats, imported documents and indexes are stored on the drive and are **not encrypted**. Protect the USB if it contains sensitive information.

Need help? See [Troubleshooting](TROUBLESHOOTING.md) or [FAQ](FAQ.md).
