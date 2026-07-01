import pytest
from pydantic import ValidationError

from integracao_tarefas.models.tarefas import (
    TaskCreateRequest,
    TaskResponse,
    TaskStatus,
    TaskUpdateRequest,
)


def test_create_accepts_all_fields() -> None:
    task = TaskCreateRequest(
        title="Documentar API",
        description="Criar documentação técnica.",
        status="in_progress",
    )

    assert task.title == "Documentar API"
    assert task.description == "Criar documentação técnica."
    assert task.status is TaskStatus.IN_PROGRESS


def test_create_applies_defaults() -> None:
    task = TaskCreateRequest(title="Documentar API")

    assert task.description is None
    assert task.status is TaskStatus.PENDING


@pytest.mark.parametrize("title", ["ab", "   ", "a" * 121])
def test_create_rejects_invalid_title(title: str) -> None:
    with pytest.raises(ValidationError):
        TaskCreateRequest(title=title)


def test_create_strips_external_title_whitespace() -> None:
    task = TaskCreateRequest(title="  Documentar API  ")

    assert task.title == "Documentar API"


def test_create_validates_title_after_stripping_whitespace() -> None:
    with pytest.raises(ValidationError):
        TaskCreateRequest(title="  ab  ")


def test_create_rejects_description_longer_than_1000_characters() -> None:
    with pytest.raises(ValidationError):
        TaskCreateRequest(title="Título válido", description="a" * 1001)


def test_create_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        TaskCreateRequest(title="Título válido", status="invalid")


def test_create_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        TaskCreateRequest(title="Título válido", unknown="value")


def test_update_accepts_each_editable_field() -> None:
    assert TaskUpdateRequest(title="Novo título").title == "Novo título"
    assert TaskUpdateRequest(description="Nova descrição").description == "Nova descrição"
    assert TaskUpdateRequest(status="completed").status is TaskStatus.COMPLETED


def test_update_rejects_empty_body() -> None:
    with pytest.raises(ValidationError, match="At least one field must be provided"):
        TaskUpdateRequest()


def test_update_rejects_null_title() -> None:
    with pytest.raises(ValidationError, match="title cannot be null"):
        TaskUpdateRequest(title=None)


def test_update_rejects_null_status() -> None:
    with pytest.raises(ValidationError, match="status cannot be null"):
        TaskUpdateRequest(status=None)


def test_update_accepts_null_description() -> None:
    update = TaskUpdateRequest(description=None)

    assert update.model_fields_set == {"description"}
    assert update.description is None


@pytest.mark.parametrize("title", ["ab", "   ", "a" * 121])
def test_update_rejects_invalid_title(title: str) -> None:
    with pytest.raises(ValidationError):
        TaskUpdateRequest(title=title)


def test_update_strips_external_title_whitespace() -> None:
    update = TaskUpdateRequest(title="  Novo título  ")

    assert update.title == "Novo título"


def test_update_rejects_description_longer_than_1000_characters() -> None:
    with pytest.raises(ValidationError):
        TaskUpdateRequest(description="a" * 1001)


def test_update_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        TaskUpdateRequest(status="invalid")


def test_update_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        TaskUpdateRequest(unknown="value")


@pytest.mark.parametrize(
    "schema",
    [TaskCreateRequest, TaskUpdateRequest, TaskResponse],
)
def test_main_schemas_include_openapi_examples(schema: type) -> None:
    examples = schema.model_json_schema().get("examples")

    assert examples
