from fastapi import FastAPI

from integracao_tarefas.routes.tarefas import router

app = FastAPI()

app.include_router(router, prefix="/tarefas/v1", tags=["tarefas"])

