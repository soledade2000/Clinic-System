#app/schemas/consulta.py
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session, sessionmaker, joinedload
from typing import List, Optional
from app import schemas, models
from app.database import get_db, engine
from app.crud import consultas as crud
from app.core.websockets import manager
import asyncio
import json
from app.schemas import CargoEnum
from app.dependencies import require_roles, get_current_user


router = APIRouter(tags=["Consultas"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Criar consulta
@router.post("/", response_model=schemas.ConsultaOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA, CargoEnum.MEDICO))])
async def create_consulta(
    consulta: schemas.ConsultaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    consulta_db = crud.criar_consulta(db, consulta, current_user)
    asyncio.create_task(manager.broadcast(json.dumps({
        "evento": "nova_consulta",
        "consulta_id": consulta_db.id
    })))
    return consulta_db


# Listar consultas (com paciente e usuário)
@router.get("/", response_model=List[schemas.ConsultaOut])
def list_consultas(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    paciente_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    query = db.query(models.Consulta).options(
        joinedload(models.Consulta.paciente),
        joinedload(models.Consulta.usuario)
    )

    # Médicos só veem suas próprias consultas
    if current_user.cargo not in [CargoEnum.ADMIN, CargoEnum.SECRETARIA]:
        query = query.filter(models.Consulta.usuario_id == current_user.id)

    if paciente_id:
        query = query.filter(models.Consulta.paciente_id == paciente_id)
    if usuario_id and current_user.cargo in [CargoEnum.ADMIN, CargoEnum.SECRETARIA]:
        query = query.filter(models.Consulta.usuario_id == usuario_id)
    if status:
        query = query.filter(models.Consulta.status == status)
    if search:
        query = query.join(models.Paciente).filter(models.Paciente.nome_completo.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()


# Atualizar consulta
@router.put("/{consulta_id}", response_model=schemas.ConsultaOut,
            dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def update_consulta(
    consulta_id: int,
    consulta: schemas.ConsultaUpdate,
    db: Session = Depends(get_db)
):
    consulta_atualizada = crud.atualizar_consulta(db, consulta_id, consulta)
    asyncio.create_task(manager.broadcast(json.dumps({
        "evento": "consulta_atualizada",
        "consulta_id": consulta_atualizada.id
    })))
    return consulta_atualizada


# Deletar consulta
@router.delete("/{consulta_id}",
               dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def delete_consulta(
    consulta_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_consulta(db, consulta_id)
    if not success:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    asyncio.create_task(manager.broadcast(json.dumps({
        "evento": "consulta_deletada",
        "consulta_id": consulta_id
    })))
    return {"msg": "Consulta excluída com sucesso"}


# WebSocket
@router.websocket("/ws")
async def consultas_ws(websocket: WebSocket, token: str = Query(...)):
    db = SessionLocal()
    await manager.connect(websocket, token=token, db=db)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        db.close()
