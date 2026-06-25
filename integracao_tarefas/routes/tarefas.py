from fastapi import APIRouter


router = APIRouter()

@router.get("/")
def health_check():
    return {"status": "running"}


@router.post("/create")
def