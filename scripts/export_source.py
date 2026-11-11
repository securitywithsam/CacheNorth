"""Create the reviewed, source-only CacheNorth export (allowlist-based) and verify it.

Writes <out>/CacheNorth-v<version>/ (staged tree), <out>/CacheNorth-v<version>-source-only.zip,
<out>/SHA256SUMS.txt, and <out>/MANIFEST.json. Fails if anything outside the allowlist, any binary or
content file, any oversized file, or any private or secret-looking text is found.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INCLUDE_FILES = [
    "README.md", "SECURITY.md", ".gitignore", "pyproject.toml", "run_offline_ai.py",
    "third_party/manifest.json",
    "launcher/StartOfflineAI.cs", "launcher/PathResolutionTests.cs", "launcher/CacheNorth.ico",
    "docs/INSTALLATION.md", "docs/BUILDING.md", "docs/CONFIGURATION.md", "docs/TROUBLESHOOTING.md",
    "docs/ARCHITECTURE.md", "docs/THIRD_PARTY_LICENSES.md", "docs/RELEASE_NOTES.md", "docs/LICENSE_RECOMMENDATION.md",
    "docs/assets/cache-north-logo.png", "docs/assets/sws-logo-original-copy.png",
    "scripts/bootstrap.ps1", "scripts/fetch_third_party.ps1", "scripts/build.ps1", "scripts/test.ps1",
    "scripts/cache_north_version_info.txt", "scripts/collect_runtime_licenses.py", "scripts/export_source.py",
    "scripts/diagnose_gpu_block_readonly.ps1", "scripts/measure_context_memory_v103.py",
    "scripts/accept_v101_stage.py", "scripts/accept_v102_gpu_policy.py", "scripts/accept_v103_context.py",
    "scripts/accept_native_shutdown_v101.py", "scripts/accept_native_xclose_v102.py",
    "scripts/accept_conversation_persistence_v101.py", "scripts/accept_failure_and_active_shutdown_v101.py",
    "scripts/capture_headless_screenshots.py", "scripts/create_cache_north_guides.py",
]
INCLUDE_GLOBS = [
    ".github/workflows/*.yml", ".github/ISSUE_TEMPLATE/*.md",
    "requirements/*.txt",
    "src/security_with_sam/*.py",
    "dashboard/*.html", "dashboard/*.css", "dashboard/*.js", "dashboard/*.png", "dashboard/*.ico",
    "tests/*.py", "tests/*.js", "tests/fixtures/*",
    "licenses/*",
]
BINARY_OK = {".png", ".ico"}  # first-party branding images only
FORBIDDEN_SUFFIXES = {".exe", ".dll", ".pyd", ".pyc", ".gguf", ".zim", ".map", ".mbtiles", ".pmtiles", ".sqlite3",
                      ".log", ".zip", ".nupkg", ".pdf", ".env", ".pem", ".key", ".pfx"}
MAX_BYTES = 2 * 1024 * 1024
PRIVATE_PATTERNS = {
    "personal path": re.compile(r"C:[\\/]{1,2}Users[\\/]{1,2}(?![<%$])\w", re.I),
    "developer name in path": re.compile(r"Samso", re.I),
    "USB volume label": re.compile(r"OFFLINE-KIT"),
    "USB serial": re.compile(r"74F6-?7862", re.I),
    "USB hardware": re.compile(r"Kingston", re.I),
    "machine id": re.compile(r"9bdbbb08b8daef0e"),
    "email address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:com|net|org|io)\b"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    "AWS key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "API key": re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    "hard-coded secret": re.compile(r"(?i)(password|secret|api_key|apikey)\s*=\s*['\"][^'\"\s]{8,}['\"]"),
}
# Reviewed exceptions: (relative path, pattern name) pairs that are intentional and harmless.
ALLOWED = {
    ("scripts/export_source.py", "*"),  # contains the patterns themselves
    ("licenses/Python-3.12.8.txt", "email address"),  # contributor address in the official, unmodifiable license text
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def collect() -> list[str]:
    files = set(INCLUDE_FILES)
    for pattern in INCLUDE_GLOBS:
        files.update(str(path.relative_to(ROOT)).replace("\\", "/") for path in ROOT.glob(pattern) if path.is_file())
    missing = [name for name in files if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit(f"Allowlisted files are missing: {missing}")
    return sorted(files)


def scan(stage: Path, files: list[str]) -> list[str]:
    problems = []
    for name in files:
        path = stage / name
        suffix = path.suffix.lower()
        if suffix in FORBIDDEN_SUFFIXES:
            problems.append(f"{name}: forbidden file type {suffix}")
        if path.stat().st_size > MAX_BYTES:
            problems.append(f"{name}: larger than {MAX_BYTES} bytes")
        if suffix in BINARY_OK:
            continue
        text = path.read_bytes()
        if b"\x00" in text:
            problems.append(f"{name}: binary content in a text file")
            continue
        decoded = text.decode("utf-8", errors="replace")
        for label, pattern in PRIVATE_PATTERNS.items():
            if (name, "*") in ALLOWED or (name, label) in ALLOWED:
                continue
            for match in pattern.finditer(decoded):
                line = decoded.count("\n", 0, match.start()) + 1
                problems.append(f"{name}:{line}: {label}: {match.group(0)[:40]}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "output" / "github-export")
    args = parser.parse_args()
    version = re.search(r'^version\s*=\s*"([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M).group(1)
    name = f"CacheNorth-v{version}"
    out = args.out.resolve()
    stage = out / name
    archive = out / f"{name}-source-only.zip"
    if stage.exists() or archive.exists():
        raise SystemExit(f"{stage} or {archive} already exists; refusing to overwrite a previous export.")
    files = collect()
    for relative in files:
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    problems = scan(stage, files)
    all_staged = sorted(str(p.relative_to(stage)).replace("\\", "/") for p in stage.rglob("*") if p.is_file())
    if all_staged != files:
        problems.append("Staged tree differs from the allowlist.")
    if problems:
        print("\n".join(problems))
        shutil.rmtree(stage)  # Only the staging folder this run created; nothing is published.
        raise SystemExit("Export blocked: review the problems above.")
    manifest = [{"path": rel, "bytes": (stage / rel).stat().st_size, "sha256": sha256(stage / rel)} for rel in files]
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for entry in manifest:
            bundle.write(stage / entry["path"], f"{name}/{entry['path']}")
    # Re-open the archive and verify every entry against the manifest.
    with zipfile.ZipFile(archive) as bundle:
        names = sorted(info.filename for info in bundle.infolist())
        expected = sorted(f"{name}/{entry['path']}" for entry in manifest)
        if names != expected:
            raise SystemExit("ZIP contents do not match the manifest.")
        for entry in manifest:
            if hashlib.sha256(bundle.read(f"{name}/{entry['path']}")).hexdigest().upper() != entry["sha256"]:
                raise SystemExit(f"ZIP entry hash mismatch: {entry['path']}")
    (out / "MANIFEST.json").write_text(json.dumps({"name": name, "version": version, "files": manifest}, indent=2), encoding="utf-8")
    (out / "SHA256SUMS.txt").write_text("".join(f"{e['sha256']}  {name}/{e['path']}\n" for e in manifest)
                                        + f"{sha256(archive)}  {archive.name}\n", encoding="utf-8")
    print(f"{len(manifest)} files, {sum(e['bytes'] for e in manifest):,} bytes -> {archive} ({archive.stat().st_size:,} bytes)")
    print(f"ZIP SHA-256: {sha256(archive)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
