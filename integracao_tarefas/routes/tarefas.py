from datetime import datetime, timezone
from itertools import count

from fastapi import APIRouter, Response
from integracao_tarefas.models.tarefas import TaskCreateRequest, TaskResponse


router = APIRouter()

tasks: list[TaskResponse] = []
task_id_sequence = count(start=1)

@router.post("/create", response_model=TaskResponse, status_code=201, summary="Criar uma tarefa",
    description="Cria uma nova tarefa com os dados informados.")
def create_task(data: TaskCreateRequest, response: Response) -> TaskResponse:
    """"
    Cria uma nova tarefa com os dados informados.
    
    Args:
        data (TaskCreateRequest): Dados da tarefa a ser criada.
        response (Response): Objeto de resposta do FastAPI.
    Returns:
        TaskResponse: Dados da tarefa criada.
    """

    now = datetime.now(timezone.utc)

    data = TaskResponse(
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
