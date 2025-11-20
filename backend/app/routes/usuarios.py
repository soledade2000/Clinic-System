from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.usuarios import Usuario
from app import schemas, models
from app.crud import usuarios as crud
from app.database import get_db
from app.core.auth import get_current_user  
from app.schemas import CargoEnum
from app.dependencies import require_roles

router = APIRouter(tags=["Usuários"])

@router.get("/me", response_model=schemas.UsuarioOut)
def read_me(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.post("/", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.criar_usuario(db, usuario)

@router.get("/", response_model=List[schemas.UsuarioOut],
            dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def list_usuarios(db: Session = Depends(get_db)):
    return crud.listar_usuarios(db)

@router.put("/{user_id}", response_model=schemas.UsuarioOut,
            dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def update_usuario(user_id: int, usuario: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    usuario_db = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    for key, value in usuario.model_dump(exclude_unset=True).items():
        setattr(usuario_db, key, value)

    db.commit()
    db.refresh(usuario_db)
    return usuario_db

@router.delete("/{user_id}",
               dependencies=[Depends(require_roles(CargoEnum.ADMIN, CargoEnum.SECRETARIA))])
def delete_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario_db = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(usuario_db)
    db.commit()
    return {"msg": f"Usuário {user_id} excluído com sucesso"}
