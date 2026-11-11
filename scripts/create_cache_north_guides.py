from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
SHOTS = ROOT / "output" / "screenshots-expansion"
LOGO = ROOT / "docs" / "assets" / "cache-north-logo.png"

NAVY = colors.HexColor("#050B12")
PANEL = colors.HexColor("#0B1B2A")
PANEL_2 = colors.HexColor("#10263A")
CYAN = colors.HexColor("#35D7FF")
WHITE = colors.HexColor("#F7FAFC")
MUTED = colors.HexColor("#B6C4D5")
GRID = colors.HexColor("#17354A")
GREEN = colors.HexColor("#4EE0A0")
AMBER = colors.HexColor("#FFC56B")

BASE = getSampleStyleSheet()
STYLES = {
    "CoverKicker": ParagraphStyle("CoverKicker", parent=BASE["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=CYAN, tracking=2.2, spaceAfter=18),
    "CoverTitle": ParagraphStyle("CoverTitle", parent=BASE["Title"], fontName="Helvetica-Bold", fontSize=36, leading=39, textColor=WHITE, spaceAfter=16),
    "CoverSub": ParagraphStyle("CoverSub", parent=BASE["Normal"], fontName="Helvetica", fontSize=15, leading=22, textColor=MUTED, spaceAfter=16),
    "H1": ParagraphStyle("H1", parent=BASE["Heading1"], fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=WHITE, spaceAfter=9),
    "H2": ParagraphStyle("H2", parent=BASE["Heading2"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=WHITE, spaceBefore=8, spaceAfter=6),
    "Kicker": ParagraphStyle("Kicker", parent=BASE["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=CYAN, tracking=1.8, spaceAfter=8),
    "Body": ParagraphStyle("Body", parent=BASE["BodyText"], fontName="Helvetica", fontSize=10.2, leading=15.2, textColor=MUTED, spaceAfter=8),
    "Small": ParagraphStyle("Small", parent=BASE["BodyText"], fontName="Helvetica", fontSize=8.2, leading=11.5, textColor=MUTED, spaceAfter=5),
    "Step": ParagraphStyle("Step", parent=BASE["BodyText"], fontName="Helvetica", fontSize=10.2, leading=15.2, textColor=WHITE, leftIndent=20, firstLineIndent=-20, spaceAfter=7),
    "Callout": ParagraphStyle("Callout", parent=BASE["BodyText"], fontName="Helvetica-Bold", fontSize=10, leading=15, textColor=WHITE),
    "Center": ParagraphStyle("Center", parent=BASE["BodyText"], fontName="Helvetica", fontSize=9, leading=13, alignment=TA_CENTER, textColor=MUTED),
}


def page_background(canvas, doc) -> None:
    canvas.saveState()
    width, height = letter
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#0E2534"))
    canvas.setLineWidth(0.35)
    for x in range(0, int(width) + 1, 24):
        canvas.line(x, 0, x, height)
    for y in range(0, int(height) + 1, 24):
        canvas.line(0, y, width, y)
    canvas.setFillColor(CYAN)
    canvas.rect(0.55 * inch, height - 0.52 * inch, width - 1.1 * inch, 1.5, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(0.55 * inch, 0.34 * inch, "SECURITY WITH SAM  /  CACHENORTH")
    canvas.drawRightString(width - 0.55 * inch, 0.34 * inch, f"{doc.footer_title.upper()}  /  {canvas.getPageNumber():02d}")
    canvas.restoreState()


def cover(title: str, subtitle: str, edition: str, tags: str) -> list:
    return [
        Spacer(1, 0.22 * inch),
        Table(
            [[Image(str(LOGO), 0.82 * inch, 0.82 * inch), Paragraph("SECURITY WITH SAM<br/><font color='#35D7FF'>CACHENORTH</font>", STYLES["Kicker"]), Paragraph(edition, STYLES["Small"])]],
            colWidths=[0.98 * inch, 3.65 * inch, 2.2 * inch],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (-1, 0), (-1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LINEBELOW", (0, 0), (-1, -1), 1, CYAN),
            ]),
        ),
        Spacer(1, 0.72 * inch),
        Paragraph("YOUR KNOWLEDGE. ANYWHERE.", STYLES["CoverKicker"]),
        Paragraph(title, STYLES["CoverTitle"]),
        Paragraph(subtitle, STYLES["CoverSub"]),
        HRFlowable(width="14%", thickness=5, color=CYAN, hAlign="LEFT", spaceBefore=4, spaceAfter=32),
        Spacer(1, 0.35 * inch),
        panel([Paragraph(tags, STYLES["Callout"]), Spacer(1, 8), Paragraph("Private local AI  •  Portable documents  •  Offline references  •  Regional maps", STYLES["Small"])]),
        Spacer(1, 0.5 * inch),
        Paragraph("Built for ordinary Windows 10 and Windows 11 computers. CPU mode is the compatibility baseline; optional Vulkan acceleration depends on the computer.", STYLES["Small"]),
        PageBreak(),
    ]


def panel(items: list, accent=CYAN) -> Table:
    inner = Table([[item] for item in items], colWidths=[6.65 * inch])
    inner.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    table = Table([[inner]], colWidths=[6.9 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("BOX", (0, 0), (-1, -1), 0.8, GRID),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    return table


def section(kicker: str, title: str, intro: str) -> list:
    return [Paragraph(kicker.upper(), STYLES["Kicker"]), Paragraph(title, STYLES["H1"]), Paragraph(intro, STYLES["Body"]), Spacer(1, 4)]


def step(number: int, heading: str, text: str) -> Paragraph:
    return Paragraph(f"<font color='#35D7FF'><b>{number:02d}</b></font>&nbsp;&nbsp;<b>{heading}</b> — {text}", STYLES["Step"])


def shot(name: str, caption: str, height: float = 3.65 * inch) -> list:
    path = SHOTS / name
    return [Image(str(path), width=6.9 * inch, height=height, kind="proportional"), Spacer(1, 5), Paragraph(caption, STYLES["Center"])]


def links(rows: list[tuple[str, str]]) -> Table:
    data = [[Paragraph(label, STYLES["Small"]), Paragraph(f'<link href="{url}" color="#35D7FF">{url}</link>', STYLES["Small"])] for label, url in rows]
    table = Table(data, colWidths=[1.55 * inch, 5.25 * inch], repeatRows=0)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def build(filename: str, title: str, story: list) -> None:
    path = OUTPUT / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.58 * inch,
        title=title,
        author="Security With Sam",
        subject="CacheNorth offline intelligence documentation",
    )
    doc.title = title
    doc.footer_title = title.removeprefix("CacheNorth ").removesuffix(" Guide")
    if doc.footer_title == "Technical and Licensing":
        doc.footer_title = "Technical"
    doc.build(story, onFirstPage=page_background, onLaterPages=page_background)


def quick_start() -> None:
    title = "CacheNorth Quick Start Guide"
    story = cover(title, "Launch private offline AI, search your own documents with source cards, and open local reference archives and maps.", f"EDITION 1.0  /  {date.today():%B %d, %Y}", "START HERE  /  FIVE-MINUTE SETUP")
    story += section("01 / Launch", "Start CacheNorth", "CacheNorth runs from its own folder and keeps normal working data beside the application. Administrator privileges, Python, Node.js, Docker, and cloud accounts are not required.")
    story += [step(1, "Connect the drive", "Open the drive in File Explorer. Its letter may change between computers; CacheNorth resolves its own location."), step(2, "Open the launcher", "Double-click <b>Launch CacheNorth.exe</b>. A branded window starts the local service and AI engine."), step(3, "Wait for Ready", "CPU startup can take several minutes on an older computer. Keep the window open while the loading messages advance."), step(4, "Use the dashboard", "The dashboard appears in the same native window when Microsoft WebView2 is available. A safe browser fallback opens when it is unavailable."), step(5, "Close cleanly", "Choose <b>Close CacheNorth</b> before removing the drive.")]
    story += [Spacer(1, 8), panel([Paragraph("First-start rule", STYLES["Callout"]), Paragraph("CPU mode is the default. Optional Vulkan can be enabled later in Settings. CacheNorth attempts one CPU fallback if Vulkan startup fails and then stops retrying.", STYLES["Body"])], GREEN), PageBreak()]
    story += section("02 / Ask", "Use private local AI", "CacheNorth automatically selects a validated local model for this computer. You can review or change the choice in Settings. Answers can contain mistakes, so verify important medical, legal, navigation, electrical, and emergency information against authoritative references.")
    story += shot("09-responsive-1366x768.png", "Actual CacheNorth dashboard at 1366 × 768, generated by the local CPU model.", 3.87 * inch)
    story += [Spacer(1, 8), step(1, "Type a question", "Press <b>Enter</b> to send. Use <b>Shift+Enter</b> for a new line."), step(2, "Continue naturally", "Follow-up questions remain in the current conversation."), step(3, "Start over", "Select New chat for a clean conversation."), PageBreak()]
    story += section("03 / Documents", "Add files and verify sources", "CacheNorth indexes searchable PDF, TXT, and Markdown files locally. Image-only PDFs need OCR in another tool before their text becomes searchable.")
    story += shot("04-document-search.png", "The document list shows filenames, searchable passage counts, page counts, and index state.", 3.5 * inch)
    story += [step(1, "Add or copy files", "Use Add documents, or copy supported files into the Data\\Documents folder and select Refresh Documents."), step(2, "Ask Documents", "Switch AI Chat to Ask Documents and ask a specific question."), step(3, "Check the cards", "Source cards come from indexed records and show the original filename, page number when available, and supporting passage."), PageBreak()]
    story += section("04 / References", "Open the library and maps", "Kiwix searches ZIM archives independently from CacheNorth document-grounded AI. GPXSee displays downloaded Mapsforge files and does not provide live navigation.")
    story += shot("03-knowledge-library.png", "Seven archives discovered dynamically with title, category, date, and size.", 3.25 * inch)
    story += [Spacer(1, 8), step(1, "Refresh", "Use Refresh All or an individual refresh after copying compatible models, documents, archives, maps, or guides."), step(2, "Choose a source", "Open an archive in Kiwix, a selected map in GPXSee, or a PDF from Guides."), step(3, "Verify current conditions", "Offline material has a publication date and maps lack live traffic, closures, and turn-by-turn guidance."), PageBreak()]
    story += section("05 / Status", "Check readiness and storage", "System Status gives ordinary users four primary cards and keeps diagnostics inside Advanced Details.")
    story += shot("08-system-status.png", "Development runs are labeled Development Storage; removable-media runs use the actual USB capacity.", 3.55 * inch)
    story += [panel([Paragraph("Safe removal", STYLES["Callout"]), Paragraph("Close CacheNorth, Kiwix, GPXSee, and opened documents. Then use Windows Safely Remove Hardware. Windows and third-party viewers may create normal temporary files, caches, or recent-file records on the computer.", STYLES["Body"])], AMBER), PageBreak()]
    story += section("06 / Help", "Where to go next", "The Guides page discovers emergency and CacheNorth PDFs at startup. Settings also opens this guide, the Troubleshooting Guide, or the complete Start Here folder without internet access.")
    story += [Paragraph("Quick checks", STYLES["H2"]), step(1, "AI still loading", "Allow more time on older CPUs and review System Status."), step(2, "Copied document missing", "Select Refresh Documents and read the progress message."), step(3, "Archive or map missing", "Confirm the file remains in Library or Maps, then refresh the section."), step(4, "Drive is read-only", "Move CacheNorth to writable media or remove physical write protection."), Spacer(1, 16), panel([Paragraph("Support information to record", STYLES["Callout"]), Paragraph("Windows version • processor • installed RAM • storage free space • exact error text • whether CPU or Vulkan was selected • recent log entries from Apps\\Offline AI\\Data\\Logs", STYLES["Body"])], CYAN), Spacer(1, 14), Paragraph("Official technical sources", STYLES["H2"]), links([("WebView2 distribution", "https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution"), ("KoboldCpp", "https://github.com/LostRuins/koboldcpp/"), ("Qwen3-4B GGUF", "https://huggingface.co/Qwen/Qwen3-4B-GGUF")])]
    build("CacheNorth Quick Start Guide.pdf", title, story)


def troubleshooting() -> None:
    title = "CacheNorth Troubleshooting Guide"
    story = cover(title, "Clear, offline recovery steps for startup, AI, documents, archives, maps, storage, and safe shutdown.", f"EDITION 1.0  /  {date.today():%B %d, %Y}", "DIAGNOSE  /  RECOVER  /  VERIFY")
    story += section("01 / Startup", "The window does not become ready", "Work through these checks in order. CacheNorth avoids automatic restart loops and reports the last confirmed failure.")
    story += [step(1, "Wait for model loading", "CPU startup is measured in seconds on the development computer and can take several minutes on older systems."), step(2, "Check writable space", "The CacheNorth data folder and Windows temporary folder must be writable. At least 512 MiB of temporary free space is required by the startup preflight."), step(3, "Check local port policy", "Security software must allow the application to bind to a random 127.0.0.1 port. CacheNorth does not listen on the network."), step(4, "Check CPU support", "The launcher selects AVX2, AVX1 compatibility, or x64 failsafe. Truly unsupported hardware receives a clear startup error."), step(5, "Read the log", "Open Apps\\Offline AI\\Data\\Logs\\koboldcpp.log and record the final error lines."), PageBreak()]
    story += section("02 / Native window", "WebView2 and browser fallback", "CacheNorth uses the installed Evergreen WebView2 Runtime when present. Windows 11 includes it and eligible updated Windows 10 systems commonly receive it. The release includes the SDK loader, not the large Fixed Version runtime.")
    story += [panel([Paragraph("If the embedded dashboard cannot start", STYLES["Callout"]), Paragraph("CacheNorth opens the exact random-token localhost URL in the default browser. It does not download or install WebView2. Keep the launcher open so managed processes shut down together.", STYLES["Body"])], GREEN), Spacer(1, 14), Paragraph("The native view blocks external navigation, new windows, downloads, permission requests, context menus, and developer tools. The browser fallback receives the same local session-token checks and security headers.", STYLES["Body"]), Spacer(1, 10), links([("WebView2 distribution", "https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution"), ("Evergreen vs Fixed", "https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/evergreen-vs-fixed-version")]), PageBreak()]
    story += section("03 / AI", "Slow, unavailable, or incomplete answers", "CPU mode is the representative baseline. Vulkan is an optional performance path and may run slower on some integrated graphics.")
    story += [step(1, "Return to CPU", "Choose CPU under Settings, AI Performance and apply the change."), step(2, "Choose a smaller model", "Open Settings and load the 1.7B model when memory is limited."), step(3, "Reduce competition", "Close memory-heavy applications and allow Windows to finish disk activity."), step(4, "Use a focused prompt", "Ask one clear task at a time. The low-memory profile limits context to 2,048 tokens."), step(5, "Stop a stalled response", "Use Stop, wait for Ready, and retry with a shorter prompt."), Spacer(1, 12), panel([Paragraph("Memory targets", STYLES["Callout"]), Paragraph("The Qwen3 1.7B model used 1.55 GiB peak process memory in an actual 2,048-context CPU test on the 32 GiB development host. This evidence supports evaluation on an 8 GiB system but does not prove 8 GiB compatibility. Physical 8 GiB and 16 GiB acceptance remains pending.", STYLES["Body"])], AMBER), PageBreak()]
    story += section("04 / Documents", "Files, indexing, and citations", "Filename filtering only narrows the visible list. Ask Documents performs full-text retrieval from the index.")
    story += shot("05-document-answer-citations.png", "Actual document-grounded answer view with source records. The final build filters weak incidental matches.", 3.35 * inch)
    story += [step(1, "Refresh copied files", "New, modified, and deleted files are synchronized safely. Duplicate content is skipped."), step(2, "Handle scanned PDFs", "If a PDF reports no searchable text, run OCR elsewhere and add the searchable copy."), step(3, "Inspect every citation", "Open the original and compare the quoted passage and page number before acting on the answer."), PageBreak()]
    story += section("05 / Library and maps", "A source does not appear or open", "Discovery uses folders relative to the current CacheNorth root, so USB drive-letter changes require no configuration.")
    story += shot("06-offline-maps.png", "All four tested Mapsforge files are discovered by filename at runtime.", 3.4 * inch)
    story += [step(1, "Confirm the extension", "Knowledge archives use .zim. Maps use .map."), step(2, "Keep the viewer", "Kiwix and the portable GPXSee files must remain in their release-relative locations."), step(3, "Refresh", "Select the relevant Refresh button after copying a file."), step(4, "Try an individual item", "Select Open in Kiwix or Open map beside the desired file."), PageBreak()]
    story += section("06 / Storage and permissions", "Read-only media, low space, and standard users", "Normal operation writes conversations, settings, indexes, documents, logs, and a WebView2 profile to the CacheNorth data folder.")
    story += [step(1, "Check the label", "Development folders show Development Storage. Removable drives show USB Storage. Internal disks show Local Storage."), step(2, "Check free space", "Keep enough room for model context, document growth, browser-profile data, and future archives."), step(3, "Use writable media", "A physically write-protected or policy-restricted drive produces a clear error before startup."), step(4, "Avoid protected folders", "Run from a user-writable drive or folder. Normal operation does not require administrator privileges."), step(5, "Check Windows temporary storage", "CacheNorth tests the system temporary directory before loading the model."), PageBreak()]
    story += section("07 / Shutdown", "Close cleanly and collect support details", "The native shell requests a graceful backend shutdown, waits, and terminates the managed backend only if necessary. KoboldCpp is owned by a Windows job object.")
    story += [panel([Paragraph("Before removing the drive", STYLES["Callout"]), Paragraph("Close CacheNorth • close Kiwix • close GPXSee • close PDFs and document viewers • wait for disk activity • use Windows Safely Remove Hardware", STYLES["Body"])], GREEN), Spacer(1, 18), Paragraph("Record these details for support", STYLES["H2"]), Paragraph("1. Exact message and time<br/>2. Windows version and whether the account is restricted<br/>3. CPU, RAM, and graphics shown in System Status<br/>4. CPU or Vulkan mode<br/>5. Storage label and free space<br/>6. Relevant koboldcpp.log lines<br/>7. Steps that reproduce the issue", STYLES["Body"]), Spacer(1, 12), Paragraph("CacheNorth makes no zero-trace claim. Windows, WebView2, a default browser, Kiwix, GPXSee, and document viewers may leave normal system records or caches.", STYLES["Body"])]
    build("CacheNorth Troubleshooting Guide.pdf", title, story)


def technical() -> None:
    title = "CacheNorth Technical and Licensing Guide"
    story = cover(title, "Architecture, compatibility evidence, security controls, dependencies, licensing status, and release limitations.", f"EDITION 1.0  /  {date.today():%B %d, %Y}", "TECHNICAL REFERENCE  /  COMMERCIAL AUDIT")
    story += section("01 / Architecture", "Portable local-first design", "The release reuses the existing Flask dashboard and Python backend inside a PyInstaller one-directory runtime. The native .NET Framework shell embeds the dashboard with WebView2 when available.")
    story += [panel([Paragraph("Launch flow", STYLES["Callout"]), Paragraph("Launch CacheNorth.exe &gt; branded native loading view &gt; random loopback port and session token &gt; CPU-default KoboldCpp start &gt; embedded dashboard or browser fallback &gt; graceful managed shutdown", STYLES["Body"])], GREEN), Spacer(1, 14), Paragraph("Runtime paths are resolved from the release root. No fixed drive letter, Windows username, Python installation, Node.js installation, Docker service, cloud service, or administrator privilege is required for normal use.", STYLES["Body"]), Paragraph("The WebView2 SDK files add roughly one megabyte to the application. Microsoft documents the Fixed Version runtime as larger than 250 MB, so CacheNorth relies on the installed Evergreen Runtime and keeps a browser fallback.", STYLES["Body"]), PageBreak()]
    story += section("02 / Native identity", "Windows application shell", "The launcher is an x64 .NET Framework Windows application with CacheNorth branding and an embedded multi-resolution icon.")
    story += [Paragraph("Identity fields", STYLES["H2"]), panel([Paragraph("Product name: CacheNorth<br/>File description: CacheNorth Offline Intelligence<br/>Company: Security With Sam<br/>Window title: CacheNorth by Security With Sam<br/>AppUserModelID: SecurityWithSam.CacheNorth", STYLES["Body"])]), Spacer(1, 14)]
    story += shot("01-native-dashboard.png", "Actual native WebView2 window from the packaged integration build.", 3.5 * inch)
    story += [PageBreak()]
    story += section("03 / Security", "Local API and content boundaries", "CacheNorth treats uploaded text as untrusted data and keeps the service on loopback.")
    story += [step(1, "Network boundary", "Waitress binds only to 127.0.0.1 on a random available port."), step(2, "Session boundary", "A random 256-bit-class token is required for every API call; host and Origin checks reject non-loopback and cross-origin requests."), step(3, "Browser hardening", "Responses use no-store, nosniff, frame denial, a restrictive content-security policy, and permissions policy."), step(4, "File boundary", "Extensions, filenames, size limits, and confined paths limit document operations."), step(5, "Prompt boundary", "Document passages are labeled untrusted; embedded role changes and commands are ignored."), step(6, "Process boundary", "The engine uses a private password, loopback binding, hidden process creation, and kill-on-close job ownership."), Spacer(1, 10), panel([Paragraph("Residual risks", STYLES["Callout"]), Paragraph("Local model output can be inaccurate. Malformed documents exercise third-party parsers. Endpoint security software may inspect files. Third-party viewers maintain their own caches and histories. Keep dependencies patched and verify sensitive answers.", STYLES["Body"])], AMBER), PageBreak()]
    story += section("04 / Compatibility and performance", "Measured and simulated evidence", "The development host was Windows 11 Pro x64 with a Ryzen 7 7800X3D, 32 GiB RAM, an RTX 3080, and AMD integrated graphics. GPU measurements are optional-path results.")
    data = [
        ["Scenario", "Evidence", "Result"],
        ["CPU model startup", "Actual, 8,192 context", "9.139 s"],
        ["Qwen3 1.7B CPU", "Actual repeated generation", "34.3-46.5 tok/s"],
        ["Qwen3 4B CPU", "Actual repeated generation", "16.7-19.7 tok/s"],
        ["Qwen3.5 4B CPU", "Actual repeated generation", "13.5-16.9 tok/s"],
        ["Qwen3 4B peak RSS", "2K / 4K / 8K context", "2.76 / 3.04 / 3.61 GiB"],
        ["Qwen3 4B CPU", "Actual load + generation", "6.344 s / 2.75 GiB peak"],
        ["Qwen3.5 4B CPU", "Actual load + generation", "6.343 s / 2.83 GiB peak"],
        ["8 GiB profile", "Simulated selection", "1.7B / 2,048 context"],
        ["16 GiB profile", "Simulated selection, measured load", "4,096 context / 3.04 GiB"],
        ["Document indexing", "Actual 36-page PDF", "0.560 s"],
        ["Document search", "Actual indexed query", "0.00158 s"],
        ["Windows 10 / older CPUs", "Static and simulated", "Hardware acceptance pending"],
    ]
    table = Table([[Paragraph(str(cell), STYLES["Small"]) for cell in row] for row in data], colWidths=[1.55 * inch, 2.75 * inch, 2.5 * inch], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PANEL_2), ("GRID", (0, 0), (-1, -1), 0.5, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [table, Spacer(1, 12), Paragraph("No 8 GiB compatibility guarantee is made until actual 8 GiB hardware testing is complete. Windows 10, older physical CPUs, and restricted enterprise environments also remain acceptance-test items.", STYLES["Body"]), PageBreak()]
    story += section("05 / Software licenses", "Redistributable runtime components", "Bundle the actual license texts and applicable notices with every commercial copy. Review source-offer obligations when publishing binaries.")
    story += [links([("KoboldCpp", "https://github.com/LostRuins/koboldcpp/"), ("KoboldCpp releases", "https://github.com/LostRuins/koboldcpp/releases"), ("Qwen3-4B GGUF", "https://huggingface.co/Qwen/Qwen3-4B-GGUF"), ("Kiwix JS PWA", "https://github.com/kiwix/kiwix-js-pwa/releases/"), ("GPXSee", "https://github.com/tumic0/GPXSee"), ("WebView2 SDK", "https://www.nuget.org/packages/Microsoft.Web.WebView2"), ("WebView2 distribution", "https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution")]), Spacer(1, 14), Paragraph("The final package includes collected Python runtime licenses, project dependency notices, and the Microsoft WebView2 SDK license. The Evergreen Runtime is supplied by Windows or the computer owner; CacheNorth does not silently install it.", STYLES["Body"]), PageBreak()]
    story += section("06 / Content licenses", "Commercial-release blockers", "Download availability does not establish permission to redistribute a work commercially. The archive and map provenance must be documented per exact file.")
    rows = [
        ["Content", "Current finding", "Commercial status"],
        ["iFixit ZIM", "iFixit publishes content under CC BY-NC-SA terms.", "BLOCKED for commercial bundle without permission"],
        ["MedlinePlus ZIM", "MedlinePlus contains public-domain and separately protected material.", "Exact archive rights review required"],
        ["Ready.gov ZIM", "U.S. government material may be public domain, but marks and third-party items can differ.", "Archive-level review required"],
        ["Simple English Wikipedia", "CC BY-SA and GFDL attribution/share-alike obligations apply.", "Comply with notices, attribution, and source terms"],
        ["Offline maps", "Provider and extract provenance are not established from filenames alone.", "BLOCKED until exact source/license is recorded"],
    ]
    licensing = Table([[Paragraph(str(cell), STYLES["Small"]) for cell in row] for row in rows], colWidths=[1.25 * inch, 3.15 * inch, 2.4 * inch], repeatRows=1)
    licensing.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PANEL_2), ("GRID", (0, 0), (-1, -1), 0.5, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [licensing, Spacer(1, 12), links([("iFixit licensing", "https://about.ifixit.com/Info/Licensing"), ("MedlinePlus content", "https://medlineplus.gov/about/using/usingcontent/"), ("Wikimedia Terms", "https://foundation.wikimedia.org/wiki/Terms_of_Use"), ("OpenStreetMap copyright", "https://www.openstreetmap.org/copyright"), ("Mapsforge downloads", "https://download.mapsforge.org/")]), PageBreak()]
    story += section("07 / Validation", "Final test evidence", "Automated tests cover security controls, dynamic discovery, storage labeling, CPU profiles, low-memory selection, path confinement, citations, settings, and API behavior.")
    story += [panel([Paragraph("Current automated result", STYLES["Callout"]), Paragraph("67 Python tests and 3 dashboard keyboard tests passed. JavaScript syntax validation also passed.", STYLES["Body"])], GREEN), Spacer(1, 14), Paragraph("Real-model evaluation", STYLES["H2"]), Paragraph("Qwen3 1.7B, Qwen3 4B, and Qwen3.5 4B each completed repeated actual CPU-only generation with its embedded GGUF chat template. The packaged v1.0.1 workflow also passed model switching, grounded sources, Refresh All, performance reporting, native shutdown, and zero-process cleanup.", STYLES["Body"]), Paragraph("KoboldCpp 1.124.2 runs from its unpacked portable layout, with the one-file executable retained as a fallback. Packaged CPU, automatic Vulkan, manual Vulkan, forced Vulkan failure with CPU recovery, and shutdown during active generation all completed without creating a new orphaned KoboldCpp extraction directory.", STYLES["Body"]), Paragraph("Actual hardware: Windows 11 CPU, NVIDIA Vulkan, AMD integrated Vulkan, document indexing/search, seven ZIM archives, four maps, ten discovered guides/help PDFs, packaged startup, native WebView2 launch, GPXSee map opening, and clean process shutdown. Simulated: memory profiles, older-CPU selectors, read-only media, unavailable ports, low temp space, special paths, and drive-letter changes.", STYLES["Body"]), PageBreak()]
    story += section("08 / Release decision", "Conditional technical readiness", "The application build is technically ready for a controlled deployment review. Commercial redistribution remains blocked by unresolved content licensing and pending acceptance environments.")
    story += [panel([Paragraph("OVERALL READINESS: CONDITIONAL", STYLES["Callout"]), Paragraph("Pass: core application, CPU baseline, hardware-aware model manager, native shell with fallback, dynamic documents, library, maps, guides, storage detection, packaging, and security controls.<br/><br/>Block: commercial shipment of iFixit and unidentified map data; archive-level content-rights review; Windows 10 and lower-memory physical acceptance; explicit USB deployment approval.", STYLES["Body"])], AMBER), Spacer(1, 18), Paragraph("Deployment controls", STYLES["H2"]), Paragraph("The release manifest inventories each proposed file, calculates SHA-256 hashes, checks destination collisions, projects remaining free space, and performs no USB write. Recheck identity, space, and collisions immediately before any approved copy.", STYLES["Body"]), Paragraph("This guide provides a technical and licensing audit summary, not legal advice. A qualified attorney should review commercial redistribution rights before sale.", STYLES["Small"])]
    build("CacheNorth Technical and Licensing Guide.pdf", title, story)


if __name__ == "__main__":
    quick_start()
    troubleshooting()
    technical()
    print(f"Created 3 guides in {OUTPUT}")
