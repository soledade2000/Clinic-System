#app/core/permissions.py
from fastapi import Depends, HTTPException, status
from app.models.usuarios import Usuario, CargoEnum
from app.core.auth import get_current_user
from app.models.token_blacklist import TokenBlacklist
from app.database import get_db
from sqlalchemy.orm import Session

def require_roles(*roles: CargoEnum):
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        if current_user.cargo not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada"
            )
        return current_user
    return role_checker

