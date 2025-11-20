# app/crud/usuarios.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models
from app.schemas import usuarios as usuario_schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_usuario(db: Session, usuario: usuario_schemas.UsuarioCreate):
    existing_user = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

    senha_hash = pwd_context.hash(usuario.senha)

    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash,
        cargo=usuario.cargo  # mantém Enum, não .value
    )
    try:
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_usuario

def listar_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def atualizar_usuario(db: Session, usuario_id: int, usuario_update: usuario_schemas.UsuarioUpdate):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Pydantic V2: usa model_dump() em vez de dict()
    updates = usuario_update.model_dump(exclude_unset=True)

    # Re-hash da senha se for alterada
    if "senha" in updates:
        updates["senha_hash"] = pwd_context.hash(updates.pop("senha"))

    # Atualiza apenas atributos existentes no modelo
    for key, value in updates.items():
        if hasattr(db_usuario, key):
            setattr(db_usuario, key, value)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        db.delete(usuario)
        db.commit()
        return True
    return False

