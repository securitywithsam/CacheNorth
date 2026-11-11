from __future__ import annotations

import hashlib
import math
import re
import shutil
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Callable, Iterable

from pypdf import PdfReader

from .security import confined_path, safe_filename


WORD_RE = re.compile(r"[\w'-]+", re.UNICODE)
MAX_DOCUMENT_BYTES = 250 * 1024 * 1024
STOP_WORDS = {
    "a", "according", "an", "and", "answer", "are", "as", "at", "be", "by", "do", "document",
    "documents", "does", "for", "from", "how", "i", "in", "is", "it", "made", "my", "of", "on",
    "or", "please", "that", "the", "this", "to", "uploaded", "was", "what", "when", "where",
    "which", "who", "why", "with", "you", "your",
}


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int | None
    text: str


@dataclass(frozen=True)
class SearchResult:
    chunk_id: int
    document_id: str
    filename: str
    page_number: int | None
    passage: str
    score: float

    def as_dict(self) -> dict[str, object]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "filename": self.filename,
            "page_number": self.page_number,
            "passage": self.passage,
            "score": self.score,
        }


def _normalize_text(value: str) -> str:
    value = value.replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def extract_pages(path: Path) -> list[ExtractedPage]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(path)
        pages: list[ExtractedPage] = []
        for index, page in enumerate(reader.pages, start=1):
            text = _normalize_text(page.extract_text() or "")
            if text:
                pages.append(ExtractedPage(index, text))
        return pages
    if suffix in {".txt", ".md"}:
        text = _normalize_text(path.read_text(encoding="utf-8", errors="replace"))
        return [ExtractedPage(None, text)] if text else []
    raise ValueError("Supported document types are PDF, TXT, and Markdown.")


def chunk_text(text: str, target_words: int = 220, overlap_words: int = 40) -> Iterable[str]:
    words = text.split()
    if not words:
        return
    step = max(1, target_words - overlap_words)
    for start in range(0, len(words), step):
        chunk = words[start : start + target_words]
        if chunk:
            yield " ".join(chunk)
        if start + target_words >= len(words):
            break


class DocumentIndex:
    def __init__(self, database: Path, documents_dir: Path):
        self.database = database
        self.documents_dir = documents_dir
        self._lock = threading.RLock()
        database.parent.mkdir(parents=True, exist_ok=True)
        documents_dir.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=20)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    stored_name TEXT NOT NULL UNIQUE,
                    sha256 TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    page_count INTEGER,
                    chunk_count INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    indexed_at INTEGER NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
                    document_id UNINDEXED,
                    filename UNINDEXED,
                    page_number UNINDEXED,
                    passage,
                    tokenize='unicode61 remove_diacritics 2'
                )
                """
            )

    def list_documents(self) -> list[dict[str, object]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                "SELECT id, filename, size_bytes, page_count, chunk_count, status, message, indexed_at "
                "FROM documents ORDER BY filename COLLATE NOCASE"
            ).fetchall()
        return [dict(row) for row in rows]

    def _hash_and_copy(self, source: BinaryIO, destination: Path) -> tuple[str, int]:
        digest = hashlib.sha256()
        total = 0
        with destination.open("wb") as output:
            while True:
                block = source.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if total > MAX_DOCUMENT_BYTES:
                    raise ValueError("This document exceeds the 250 MB safety limit.")
                digest.update(block)
                output.write(block)
        return digest.hexdigest(), total

    def add_stream(
        self,
        original_name: str,
        stream: BinaryIO,
        progress: Callable[[int, str], None] | None = None,
    ) -> dict[str, object]:
        filename = safe_filename(original_name)
        document_id = uuid.uuid4().hex
        stored_name = f"{document_id}_{filename}"
        destination = confined_path(self.documents_dir, self.documents_dir / stored_name)
        try:
            sha256, size_bytes = self._hash_and_copy(stream, destination)
            with self._lock, self._connect() as connection:
                duplicate = connection.execute(
                    "SELECT id FROM documents WHERE sha256=? ORDER BY indexed_at DESC LIMIT 1", (sha256,)
                ).fetchone()
            if duplicate is not None:
                destination.unlink(missing_ok=True)
                existing = self.get_document(str(duplicate["id"]))
                existing["duplicate"] = True
                return existing
            return self._index_file(document_id, filename, stored_name, destination, sha256, size_bytes, progress)
        except Exception:
            destination.unlink(missing_ok=True)
            raise

    def _index_file(
        self,
        document_id: str,
        filename: str,
        stored_name: str,
        path: Path,
        sha256: str,
        size_bytes: int,
        progress: Callable[[int, str], None] | None,
    ) -> dict[str, object]:
        if progress:
            progress(10, "Extracting text")
        pages = extract_pages(path)
        if not pages:
            page_count = len(PdfReader(path).pages) if path.suffix.lower() == ".pdf" else None
            if path.suffix.lower() == ".pdf":
                message = "No selectable text was found. This PDF may be scanned and require OCR."
            else:
                message = "The document is empty or contains no searchable text."
            with self._lock, self._connect() as connection:
                connection.execute(
                    "INSERT INTO documents VALUES(?, ?, ?, ?, ?, ?, 0, 'unsupported', ?, ?)",
                    (document_id, filename, stored_name, sha256, size_bytes, page_count, message, int(time.time())),
                )
            return self.get_document(document_id)

        page_count = len(PdfReader(path).pages) if path.suffix.lower() == ".pdf" else None
        chunks: list[tuple[str, str, str, str]] = []
        for page in pages:
            for passage in chunk_text(page.text):
                chunks.append((document_id, filename, str(page.page_number or ""), passage))
        if progress:
            progress(70, "Building search index")
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT INTO documents VALUES(?, ?, ?, ?, ?, ?, ?, 'ready', '', ?)",
                (
                    document_id,
                    filename,
                    stored_name,
                    sha256,
                    size_bytes,
                    page_count,
                    len(chunks),
                    int(time.time()),
                ),
            )
            connection.executemany(
                "INSERT INTO chunks(document_id, filename, page_number, passage) VALUES(?, ?, ?, ?)", chunks
            )
        if progress:
            progress(100, "Ready")
        return self.get_document(document_id)

    def get_document(self, document_id: str) -> dict[str, object]:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        if row is None:
            raise KeyError("Document not found.")
        return dict(row)

    def original_path(self, document_id: str) -> Path:
        document = self.get_document(document_id)
        return confined_path(self.documents_dir, self.documents_dir / str(document["stored_name"]))

    def remove(self, document_id: str) -> None:
        path = self.original_path(document_id)
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM chunks WHERE document_id=?", (document_id,))
            connection.execute("DELETE FROM documents WHERE id=?", (document_id,))
        path.unlink(missing_ok=True)

    def sync_folder(self, progress: Callable[[int, str], None] | None = None) -> dict[str, int]:
        """Reconcile supported files copied directly into the portable Documents folder."""
        if not self.documents_dir.is_dir():
            raise FileNotFoundError(
                "The Documents folder is unavailable. Existing index data was preserved; reconnect the storage and refresh again."
            )
        supported = {".pdf", ".txt", ".md"}
        files = {
            path.name: path
            for path in self.documents_dir.iterdir()
            if path.is_file() and path.suffix.lower() in supported
        }
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT * FROM documents").fetchall()
        by_stored_name = {str(row["stored_name"]): dict(row) for row in rows}
        removed = updated = added = duplicates = errors = 0

        missing = [row for name, row in by_stored_name.items() if name not in files]
        for row in missing:
            with self._lock, self._connect() as connection:
                connection.execute("DELETE FROM chunks WHERE document_id=?", (row["id"],))
                connection.execute("DELETE FROM documents WHERE id=?", (row["id"],))
            removed += 1

        total = max(1, len(files))
        for number, (stored_name, path) in enumerate(sorted(files.items()), start=1):
            if progress:
                progress(round((number - 1) * 100 / total), f"Checking {path.name}")
            try:
                digest = hashlib.sha256()
                size_bytes = 0
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        size_bytes += len(block)
                        if size_bytes > MAX_DOCUMENT_BYTES:
                            raise ValueError("This document exceeds the 250 MB safety limit.")
                        digest.update(block)
                sha256 = digest.hexdigest()
                existing = by_stored_name.get(stored_name)
                if existing and existing["sha256"] == sha256:
                    continue
                with self._lock, self._connect() as connection:
                    duplicate = connection.execute(
                        "SELECT id FROM documents WHERE sha256=? AND stored_name<>? LIMIT 1",
                        (sha256, stored_name),
                    ).fetchone()
                if duplicate is not None:
                    duplicates += 1
                    continue
                if existing:
                    document_id = str(existing["id"])
                    filename = str(existing["filename"])
                    with self._lock, self._connect() as connection:
                        connection.execute("DELETE FROM chunks WHERE document_id=?", (document_id,))
                        connection.execute("DELETE FROM documents WHERE id=?", (document_id,))
                    updated += 1
                else:
                    document_id = uuid.uuid4().hex
                    filename = safe_filename(path.name)
                    added += 1
                self._index_file(
                    document_id, filename, stored_name, path, sha256, size_bytes, progress=None
                )
            except Exception:
                errors += 1
        if progress:
            progress(100, "Document refresh complete")
        return {
            "added": added,
            "updated": updated,
            "removed": removed,
            "duplicates": duplicates,
            "errors": errors,
        }

    @staticmethod
    def _fts_query(query: str) -> str:
        terms = [
            match.group(0).lower()
            for match in WORD_RE.finditer(query)
            if len(match.group(0)) > 1 and match.group(0).lower() not in STOP_WORDS
        ]
        terms = list(dict.fromkeys(terms))[:16]
        if not terms:
            raise ValueError("Enter at least one searchable word.")
        return " OR ".join(f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms)

    def search(self, query: str, limit: int = 6) -> list[SearchResult]:
        expression = self._fts_query(query)
        query_terms = {
            match.group(0).lower()
            for match in WORD_RE.finditer(query)
            if match.group(0).lower() not in STOP_WORDS
        }
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT rowid, document_id, filename, page_number, passage, bm25(chunks) AS score
                FROM chunks WHERE chunks MATCH ? ORDER BY score LIMIT ?
                """,
                (expression, max(1, min(limit, 12))),
            ).fetchall()
        candidates: list[tuple[int, SearchResult]] = []
        for row in rows:
            passage_terms = {match.group(0).lower() for match in WORD_RE.finditer(row["passage"])}
            overlap = len(query_terms & passage_terms)
            if not overlap:
                continue
            candidates.append(
                (
                    overlap,
                    SearchResult(
                    chunk_id=row["rowid"],
                    document_id=row["document_id"],
                    filename=row["filename"],
                    page_number=int(row["page_number"]) if row["page_number"] else None,
                    passage=row["passage"],
                    score=float(row["score"]),
                    ),
                )
            )
        if not candidates:
            return []
        strongest_overlap = max(overlap for overlap, _result in candidates)
        minimum_overlap = math.ceil(strongest_overlap / 2) if strongest_overlap >= 3 else 1
        return [result for overlap, result in candidates if overlap >= minimum_overlap][:limit]

    def rebuild(self, progress: Callable[[int, str], None] | None = None) -> None:
        existing = self.list_documents()
        total = max(1, len(existing))
        for index, item in enumerate(existing):
            document_id = str(item["id"])
            document = self.get_document(document_id)
            path = self.original_path(document_id)
            pages = extract_pages(path)
            chunks = [
                (document_id, document["filename"], str(page.page_number or ""), passage)
                for page in pages
                for passage in chunk_text(page.text)
            ]
            with self._lock, self._connect() as connection:
                connection.execute("DELETE FROM chunks WHERE document_id=?", (document_id,))
                connection.executemany(
                    "INSERT INTO chunks(document_id, filename, page_number, passage) VALUES(?, ?, ?, ?)", chunks
                )
                connection.execute(
                    "UPDATE documents SET chunk_count=?, status=?, message=?, indexed_at=? WHERE id=?",
                    (
                        len(chunks),
                        "ready" if chunks else "unsupported",
                        "" if chunks else "No searchable text was found.",
                        int(time.time()),
                        document_id,
                    ),
                )
            if progress:
                progress(round((index + 1) * 100 / total), f"Indexed {index + 1} of {len(existing)} documents")
