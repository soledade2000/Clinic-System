# app/core/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from pydantic import BaseModel

from app.schemas.usuarios import UsuarioOut, UsuarioCreate
from app.database import get_db
from app.models.usuarios import Usuario
from app.core.security import create_access_token
from app.core.config import SECRET_KEY, ALGORITHM

# ---------------- Schemas ----------------
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UsuarioOut

# ---------------- Configurações ----------------
router = APIRouter(tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ---------------- Current User (OAuth2) ----------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user:
        raise credentials_exception
    return user

# ---------------- Current User para WebSocket ----------------
async def get_current_user_from_token(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user:
        raise credentials_exception
    return user

# ---------------- Registro de usuário ----------------
@router.post("/register", response_model=LoginResponse)
def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Checa se senhas batem
    if usuario.senha != usuario.confirma_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As senhas não coincidem"
        )

    # Checa se email já existe
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )

    # Cria usuário
    hashed_password = pwd_context.hash(usuario.senha)
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        cargo=usuario.cargo,
        ativo=usuario.ativo,
        senha_hash=hashed_password
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    # Gera token
    access_token = create_access_token(data={"sub": str(novo_usuario.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UsuarioOut.model_validate(novo_usuario)
    }

# ---------------- Login ----------------
@router.post("/login", response_model=LoginResponse)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == username).first()
    if not usuario or not pwd_context.verify(password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(usuario.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UsuarioOut.model_validate(usuario)
    }
