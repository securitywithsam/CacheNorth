from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfWriter

from security_with_sam.documents import DocumentIndex, chunk_text, extract_pages


def make_index(kit_root: Path) -> DocumentIndex:
    product = kit_root / "Apps" / "Offline AI"
    return DocumentIndex(product / "Data" / "Index" / "documents.sqlite3", product / "Data" / "Documents")


def test_chunking_has_overlap_and_preserves_content():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = list(chunk_text(text, target_words=100, overlap_words=20))
    assert len(chunks) > 5
    assert "word80" in chunks[0] and "word80" in chunks[1]
    assert "word499" in chunks[-1]


def test_text_document_index_search_and_source_fields(kit_root: Path):
    index = make_index(kit_root)
    result = index.add_stream(
        "Emergency Notes.txt",
        io.BytesIO(b"Turn off the main breaker before inspecting damaged household wiring. Verify power is absent."),
    )
    assert result["status"] == "ready"
    matches = index.search("main breaker damaged wiring")
    assert matches
    assert matches[0].filename == "Emergency Notes.txt"
    assert "main breaker" in matches[0].passage
    assert matches[0].page_number is None


def test_no_relevant_source_returns_empty(kit_root: Path):
    index = make_index(kit_root)
    index.add_stream("plants.md", io.BytesIO(b"Tomatoes need sunlight and regular watering."))
    assert index.search("circuit breaker voltage") == []


def test_generic_document_words_do_not_create_false_citations(kit_root: Path):
    index = make_index(kit_root)
    index.add_stream("records.md", io.BytesIO(b"Keep important documents in a waterproof container."))
    assert index.search("According to my uploaded documents, what is the capital of Portugal?") == []


def test_strongly_matching_source_filters_weak_incidental_matches(kit_root: Path):
    index = make_index(kit_root)
    index.add_stream("county.md", io.BytesIO(b"Cedar County winter center address is Pine Street. Generator fuel lasts 36 hours."))
    index.add_stream("generic.md", io.BytesIO(b"General winter preparedness advice includes warm clothing."))
    matches = index.search("Summarize Cedar County winter preparedness, address, and generator details.")
    assert matches
    assert {match.filename for match in matches} == {"county.md"}


def test_blank_pdf_is_reported_as_ocr_candidate(kit_root: Path, tmp_path: Path):
    blank = tmp_path / "scan.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with blank.open("wb") as stream:
        writer.write(stream)
    index = make_index(kit_root)
    with blank.open("rb") as stream:
        result = index.add_stream("scan.pdf", stream)
    assert result["status"] == "unsupported"
    assert "OCR" in result["message"]
    assert result["page_count"] == 1


def test_duplicate_content_is_reused_without_duplicate_file(kit_root: Path):
    index = make_index(kit_root)
    first = index.add_stream("first.txt", io.BytesIO(b"Identical CacheNorth document content."))
    second = index.add_stream("renamed-copy.txt", io.BytesIO(b"Identical CacheNorth document content."))
    assert second["id"] == first["id"]
    assert second["duplicate"] is True
    assert len(index.list_documents()) == 1
    assert len(list(index.documents_dir.iterdir())) == 1


def test_remove_deletes_file_and_index_rows(kit_root: Path):
    index = make_index(kit_root)
    document = index.add_stream("remove.txt", io.BytesIO(b"A unique phrase for removal testing."))
    original = index.original_path(str(document["id"]))
    assert original.exists()
    index.remove(str(document["id"]))
    assert not original.exists()
    assert index.search("unique phrase") == []


def test_sync_folder_adds_updates_and_removes_copied_files(kit_root: Path):
    index = make_index(kit_root)
    copied = index.documents_dir / "field notes.txt"
    copied.write_text("The portable radio uses three batteries.", encoding="utf-8")
    assert index.sync_folder()["added"] == 1
    assert index.search("three batteries")[0].filename == "field notes.txt"
    copied.write_text("The portable radio uses four batteries.", encoding="utf-8")
    assert index.sync_folder()["updated"] == 1
    assert index.search("four batteries")
    assert all("three" not in match.passage for match in index.search("three batteries"))
    copied.unlink()
    assert index.sync_folder()["removed"] == 1
    assert index.list_documents() == []
