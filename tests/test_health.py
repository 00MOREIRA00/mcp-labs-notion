import asyncio
import json
from typing import Any

from integracao_tarefas.main import app


def get(path: str) -> tuple[int, bytes]:
    messages: list[dict[str, Any]] = []
    request_sent = False

    async def receive() -> dict[str, Any]:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }

    asyncio.run(app(scope, receive, send))

    start = next(message for message in messages if message["type"] == "http.response.start")
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return start["status"], body


def test_health_returns_ok() -> None:
    status, body = get("/health")

    assert status == 200
    assert json.loads(body) == {"status": "ok"}


def test_documentation_routes_are_available() -> None:
    assert get("/docs")[0] == 200
    assert get("/redoc")[0] == 200
    assert get("/openapi.json")[0] == 200


def test_openapi_contains_application_metadata() -> None:
    schema = app.openapi()

    assert schema["info"]["title"] == "API de Tarefas"
    assert schema["info"]["description"] == "API REST para gerenciamento de tarefas."
    assert schema["info"]["version"] == "1.0.0"


def test_openapi_contains_health_route_with_health_tag() -> None:
    schema = app.openapi()

    assert schema["paths"]["/health"]["get"]["tags"] == ["Health"]


def test_task_routes_use_api_v1_prefix_and_tasks_tag() -> None:
    schema = app.openapi()
    task_paths = [path for path in schema["paths"] if path != "/health"]

    assert task_paths
    assert all(path.startswith("/api/v1/") for path in task_paths)
    assert all(
        operation["tags"] == ["Tasks"]
        for path in task_paths
        for operation in schema["paths"][path].values()
    )
