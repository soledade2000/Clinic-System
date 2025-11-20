# app/routes/pacientes.py
from fastapi import (
    APIRouter, Depends, HTTPException, status,
    UploadFile, File, Form, BackgroundTasks
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import os, uuid

from app import schemas, models
from app.database import get_db
from app.crud import paciente as paciente_crud
from app.core.websockets import manager
from app.schemas import CargoEnum
from app.dependencies import require_roles

router = APIRouter(tags=["Pacientes"])

# ===============================
# 🔹 Funções auxiliares
# ===============================
def calcular_idade(data_nascimento: date) -> int:
    hoje = date.today()
    idade = hoje.year - data_nascimento.year
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade

# ===============================
# 🔹 CRUD de Pacientes
# ===============================
@router.post("/", response_model=schemas.PacienteOut,
             dependencies=[Depends(require_roles(
                 CargoEnum.ADMIN, CargoEnum.SECRETARIA,
                 CargoEnum.MEDICO, CargoEnum.PSICOLOGO,
                 CargoEnum.FISIOTERAPIA, CargoEnum.NUTRICIONISTA, CargoEnum.CLINICO
             ))])
def create_paciente(
    paciente: schemas.PacienteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    idade = calcular_idade(paciente.data_nascimento)

    idade_responsavel = None
    if paciente.data_nascimento_responsavel:
        idade_responsavel = calcular_idade(paciente.data_nascimento_responsavel)

    paciente_db = models.Paciente(
        **paciente.dict(exclude={"idade", "idade_responsavel"}),
        idade=idade,
        idade_responsavel=idade_responsavel
    )
    db.add(paciente_db)
    db.commit()
    db.refresh(paciente_db)

    background_tasks.add_task(
        manager.broadcast, f"Novo paciente cadastrado: {paciente_db.nome_completo}"
    )
    return paciente_db


@router.get("/", response_model=List[schemas.PacienteOut],
            dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def list_pacientes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None
):
    query = db.query(models.Paciente)
    if search:
        query = query.filter(models.Paciente.nome_completo.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


@router.put("/{paciente_id}", response_model=schemas.PacienteOut,
            dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def update_paciente(
    paciente_id: int,
    paciente: schemas.PacienteUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    update_data = paciente.dict(exclude_unset=True)
    if "data_nascimento" in update_data:
        update_data["idade"] = calcular_idade(update_data["data_nascimento"])
    if "data_nascimento_responsavel" in update_data:
        update_data["idade_responsavel"] = calcular_idade(update_data["data_nascimento_responsavel"])

    paciente_update_obj = schemas.PacienteUpdate(**update_data)
    paciente_db = paciente_crud.atualizar_paciente(db, paciente_id, paciente_update_obj)
    if not paciente_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    background_tasks.add_task(
        manager.broadcast, f"Paciente atualizado: {paciente_db.nome_completo}"
    )
    return paciente_db


@router.delete("/{paciente_id}",
               dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def delete_paciente(
    paciente_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    success = paciente_crud.delete_paciente(db, paciente_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    background_tasks.add_task(
        manager.broadcast, f"Paciente deletado: ID {paciente_id}"
    )
    return {"msg": "Paciente excluído com sucesso"}

# ===============================
# 🔹 Atualizar forma de pagamento
# ===============================
@router.patch("/{paciente_id}/pagamento",
              dependencies=[Depends(require_roles(CargoEnum.MEDICO, CargoEnum.SECRETARIA, CargoEnum.ADMIN))])
def atualizar_forma_pagamento(paciente_id: int, payload: dict, db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    forma = payload.get("forma_pagamento")
    if not forma:
        raise HTTPException(status_code=400, detail="Forma de pagamento inválida")

    paciente.forma_pagamento = forma
    db.commit()
    db.refresh(paciente)
    return {"msg": "Forma de pagamento atualizada com sucesso", "forma_pagamento": paciente.forma_pagamento}


# ===============================
# 🔹 Uploads e Downloads de arquivos
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/{paciente_id}/upload",
             dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA, CargoEnum.MEDICO))])
async def upload_file(paciente_id: int, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo inválido ou sem nome")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Arquivo muito grande (máx. 10MB)")

    paciente_dir = os.path.join(UPLOAD_DIR, str(paciente_id))
    os.makedirs(paciente_dir, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(paciente_dir, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "path": f"/pacientes/{paciente_id}/download/{filename}"}


@router.get("/{paciente_id}/list",
            dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA, CargoEnum.MEDICO))])
def list_files(paciente_id: int):
    paciente_dir = os.path.join(UPLOAD_DIR, str(paciente_id))
    if not os.path.exists(paciente_dir):
        return {"files": []}
    files = [{"filename": f, "url": f"/pacientes/{paciente_id}/download/{f}"} for f in os.listdir(paciente_dir)]
    return {"files": files}


@router.get("/{paciente_id}/download/{filename}",
            dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA, CargoEnum.MEDICO))])
def download_file(paciente_id: int, filename: str):
    safe_filename = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, str(paciente_id), safe_filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(path, filename=safe_filename)


@router.delete("/{paciente_id}/delete/{filename}",
               dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def delete_file(paciente_id: int, filename: str):
    safe_filename = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, str(paciente_id), safe_filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    os.remove(path)
    return {"detail": "Arquivo excluído com sucesso"}


# ===============================
# 🔹 Upload de PDF (Ficha do Paciente)
# ===============================
@router.post("/upload_pdf",
             dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA, CargoEnum.MEDICO))])
async def upload_pdf_ficha(
    paciente_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Se paciente_id for informado, associa o PDF ao paciente.
    Caso contrário, cria novo paciente automaticamente.
    """
    uploads_dir = os.path.join(UPLOAD_DIR, "pdfs")
    os.makedirs(uploads_dir, exist_ok=True)

    # Salva o arquivo de forma assíncrona
    filename = (file.filename or f"upload_{uuid.uuid4().hex}.pdf").replace(" ", "_")
    filepath = os.path.join(uploads_dir, filename)
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    # Se tiver paciente_id, verifica se existe
    paciente = None
    if paciente_id:
        paciente = paciente_crud.get_paciente(db, paciente_id)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
    else:
        # Cria novo paciente básico
        novo = models.Paciente(nome_completo=filename.split(".")[0])
        db.add(novo)
        db.commit()
        db.refresh(novo)
        paciente = novo

    # Salva referência ao PDF no paciente
    paciente.ficha_pdf = filename # type: ignore
    db.add(paciente)
    db.commit()

    return {"success": True, "paciente_id": paciente.id, "filename": filename}
