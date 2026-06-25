from datetime import datetime
from enum import Enum
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints



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
    model_config = ConfigDict(extra="forbid")

    title: TaskTitle
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus = TaskStatus.PENDING

class TaskCreateResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime