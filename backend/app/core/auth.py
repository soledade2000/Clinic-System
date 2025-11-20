#app/core/auth
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime

from app.database import get_db
from app.models.usuarios import Usuario
from app.models.token_blacklist import TokenBlacklist
from app.schemas import UsuarioCreate, UsuarioOut, Token
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(tags=["Auth"])

# -------------------
# Utils
# -------------------
def get_user_by_id(db: Session, user_id: int) -> Optional[Usuario]:
    if not user_id:
        return None
    return db.query(Usuario).filter(Usuario.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[Usuario]:
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or not verify_password(password, user.senha_hash):
        return None
    return user


def is_token_blacklisted(db: Session, jti: str) -> bool:
    return db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first() is not None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Garante que jti exista
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (jti ausente)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Checa blacklist
    if is_token_blacklisted(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revogado (logout realizado)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (sub ausente)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = int(sub)

    user = get_user_by_id(db, sub)
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo ou inexistente",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# -------------------
# Rotas
# -------------------
@router.post("/register", response_model=UsuarioOut)
def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    def get_user_by_email(db: Session, email: Optional[str]) -> Optional[Usuario]:
        if not email:
            return None
        return db.query(Usuario).filter(Usuario.email == email).first()

    if get_user_by_email(db, usuario.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )

    hashed_password = hash_password(usuario.senha)
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        cargo=usuario.cargo,
        ativo=True,
        senha_hash=hashed_password
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@router.post("/login", response_model=Token)
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str = Form(...), db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Garante que jti exista
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido (jti ausente)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if is_token_blacklisted(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token já revogado (logout realizado)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (sub ausente)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(user_id)

    user = get_user_by_id(db, user_id)
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo ou inexistente",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_access = create_access_token({"sub": user.id})
    new_refresh = create_refresh_token({"sub": user.id})
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}


@router.post("/logout")
def logout(current_user: Usuario = Depends(get_current_user), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    jti = payload.get("jti")
    if jti:
        db.add(TokenBlacklist(jti=jti, created_at=datetime.utcnow()))
        db.commit()

    return {"msg": "Logout realizado com sucesso."}


@router.get("/me", response_model=UsuarioOut)
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    return current_user
