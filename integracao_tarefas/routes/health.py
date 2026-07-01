from fastapi import APIRouter


router = APIRouter()


@router.get(
    "/health",
    summary="Verificar saúde da aplicação",
    description="Confirma que a aplicação está em execução.",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
