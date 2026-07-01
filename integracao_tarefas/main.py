from fastapi import FastAPI

from integracao_tarefas.routes.health import router as health_router
from integracao_tarefas.routes.tarefas import router as tasks_router

tags_metadata = [
    {
        "name": "Health",
        "description": "Verificação da disponibilidade da aplicação.",
    },
    {
        "name": "Tasks",
        "description": "Operações de gerenciamento de tarefas.",
    },
]

app = FastAPI(
    title="API de Tarefas",
    description="API REST para gerenciamento de tarefas.",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.include_router(health_router, tags=["Health"])
app.include_router(tasks_router, prefix="/api/v1", tags=["Tasks"])
