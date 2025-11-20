from fastapi import APIRouter

router = APIRouter()

@router.get("/uploads/teste")
def teste_uploads():
    return {"status": "ok", "message": "Uploads route funcionando!"}
