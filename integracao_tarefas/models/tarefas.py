from datetime import datetime
from enum import Enum
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator



class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

TaskTitle = Annotated [
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=120
    )
]

class TaskCreateRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "title": "Documentar API de tarefas",
                    "description": "Gerar a documentação técnica da API.",
                    "status": "pending",
                }
            ]
        },
    )

    title: TaskTitle
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus = TaskStatus.PENDING

class TaskResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "title": "Documentar API de tarefas",
                    "description": "Gerar a documentação técnica da API.",
                    "status": "pending",
                    "created_at": "2026-06-30T14:00:00Z",
                    "updated_at": "2026-06-30T14:00:00Z",
                }
            ]
        }
    )

    id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

class TaskUpdateRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "status": "in_progress",
                }
            ]
        },
    )

    title: TaskTitle | None = None
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "TaskUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title cannot be null")

        if "status" in self.model_fields_set and self.status is None:
            raise ValueError("status cannot be null")

        return self
