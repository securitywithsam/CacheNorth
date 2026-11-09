from __future__ import annotations

import io
from pathlib import Path

from security_with_sam.app import create_app
from security_with_sam.config import AppPaths


class FakeEngine:
    port = 5001
    mode = "running"
    message = "Ready"

    def status(self):
        return {"state": "running", "message": "Ready", "mode": "cpu", "port": 5001, "model": "test.gguf"}

    def find_executable(self):
        return Path("koboldcpp-nocuda.exe")

    def find_model(self):
        return Path("test.gguf")

    def stream_chat(self, messages, max_tokens=None):
        yield "Local "
        yield "answer"

    def stop_generation(self):
        return None


def client_for(kit_root: Path):
    dashboard = kit_root / "Apps" / "Offline AI" / "Dashboard"
    (dashboard / "index.html").write_text("dashboard", encoding="utf-8")
    app, state = create_app(AppPaths.from_root(kit_root), FakeEngine())
    app.testing = True
    return app.test_client(), state.token


def headers(token: str):
    return {"X-SWS-Token": token, "Host": "127.0.0.1"}


def test_api_rejects_missing_token(kit_root: Path):
    client, _token = client_for(kit_root)
    assert client.get("/api/documents", headers={"Host": "127.0.0.1"}).status_code == 403


def test_api_rejects_non_loopback_host(kit_root: Path):
    client, token = client_for(kit_root)
    assert client.get("/api/documents", headers={"Host": "192.168.1.8", "X-SWS-Token": token}).status_code == 403


def test_api_rejects_cross_origin_request(kit_root: Path):
    client, token = client_for(kit_root)
    response = client.get(
        "/api/documents",
        headers={"Host": "127.0.0.1", "Origin": "https://malicious.example", "X-SWS-Token": token},
    )
    assert response.status_code == 403


def test_upload_search_and_grounded_no_answer(kit_root: Path):
    client, token = client_for(kit_root)
    response = client.post(
        "/api/documents/add",
        headers=headers(token),
        data={"file": (io.BytesIO(b"The blue valve closes the test water line."), "manual.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    chat = client.post(
        "/api/chat",
        headers=headers(token),
        json={"message": "What color is the valve?", "mode": "documents"},
    )
    assert chat.status_code == 200
    assert chat.mimetype == "application/x-ndjson"

    no_answer = client.post(
        "/api/chat",
        headers=headers(token),
        json={"message": "What is the moon made of?", "mode": "documents"},
    )
    assert no_answer.get_json()["sources"] == []
    assert "do not contain enough information" in no_answer.get_json()["answer"]


def test_refresh_documents_indexes_files_copied_into_folder(kit_root: Path):
    client, token = client_for(kit_root)
    documents = kit_root / "Apps" / "Offline AI" / "Data" / "Documents"
    (documents / "copied.md").write_text("A hand-crank radio works without grid power.", encoding="utf-8")
    response = client.post("/api/documents/refresh", headers=headers(token))
    assert response.status_code == 200
    assert response.get_json()["result"]["added"] == 1
    listed = client.get("/api/documents", headers=headers(token)).get_json()
    assert listed[0]["filename"] == "copied.md"
