from __future__ import annotations

import hmac
import re
from pathlib import Path


ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".md"}
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._ ()\[\]-]+")


def constant_time_token_matches(expected: str, supplied: str | None) -> bool:
    return bool(supplied) and hmac.compare_digest(expected, supplied)


def safe_filename(name: str) -> str:
    name = Path(name).name.strip().replace("\x00", "")
    cleaned = SAFE_NAME_RE.sub("_", name).strip(" .")
    if not cleaned:
        raise ValueError("The document filename is empty or unsupported.")
    suffix = Path(cleaned).suffix.lower()
    if suffix not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValueError("Supported document types are PDF, TXT, and Markdown.")
    return cleaned[:180]


def confined_path(base: Path, candidate: Path) -> Path:
    base_resolved = base.resolve()
    candidate_resolved = candidate.resolve()
    try:
        candidate_resolved.relative_to(base_resolved)
    except ValueError as exc:
        raise ValueError("The requested path is outside the permitted data folder.") from exc
    return candidate_resolved


def allowed_local_host(host: str | None) -> bool:
    if not host:
        return False
    hostname = host.rsplit(":", 1)[0].strip("[]").lower()
    return hostname in {"127.0.0.1", "localhost", "::1"}
