# app/uploads/uploads.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from app.dependencies import require_roles, CargoEnum
import os
import uuid
import shutil

router = APIRouter(tags=["Uploads"])

# Diretório absoluto para uploads
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/upload/", dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo inválido ou sem nome")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Arquivo muito grande (máx. 10MB)")

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(filepath, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")

    return {"filename": filename, "path": filepath}

@router.get("/download/{filename}", dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def download_file(filename: str):
    safe_filename = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, safe_filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(path)
