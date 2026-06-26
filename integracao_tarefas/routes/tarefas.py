from datetime import datetime, timezone
from itertools import count

from fastapi import APIRouter, Response
from integracao_tarefas.models.tarefas import TaskCreateResponse, TaskCreateRequest


router = APIRouter()

tasks: list[TaskCreateResponse] = []
task_id_sequence = count(start=1)

@router.get("/health")
def health_check():
    return {"status": "running"}


@router.post("/create", response_model=TaskCreateResponse, status_code=201, summary="Criar uma tarefa",
    description="Cria uma nova tarefa com os dados informados.")
def create_task(data: TaskCreateRequest, response: Response) -> TaskCreateResponse:
    """"
    Cria uma nova tarefa com os dados informados.
    
    Args:
        data (TaskCreateRequest): Dados da tarefa a ser criada.
        response (Response): Objeto de resposta do FastAPI.
    Returns:
        TaskCreateResponse: Dados da tarefa criada.
    """

    now = datetime.now(timezone.utc)

    data = TaskCreateResponse(
        id=next(task_id_sequence),
        title=data.title,
        description=data.description,
        status=data.status,
        created_at=now,
        updated_at=now
    )
    tasks.append(data)
    response.headers["Location"] = f"/api/v1/tasks/{data.id}"
    return data
