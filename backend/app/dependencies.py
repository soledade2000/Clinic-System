# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app import models, database
from app.schemas.enums import CargoEnum
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# ---------------- Configurações ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
# ---------------- Usuário autenticado ----------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
) -> models.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# ---------------- Verificação de permissões ----------------
def require_roles(*roles: CargoEnum):
    def role_checker(current_user: models.Usuario = Depends(get_current_user)):
        if current_user.cargo not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada para o cargo '{current_user.cargo}'"
            )
        return current_user
    return role_checker
