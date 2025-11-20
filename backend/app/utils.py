# app/utils.py
from passlib.context import CryptContext # type: ignore
from datetime import datetime, timedelta
from jose import jwt # type: ignore
import os

# ---------------- Configurações ----------------
SECRET_KEY = os.getenv("SECRET_KEY", "SECRET_KEY")  # ideal usar .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 dia


# ---------------- Contexto de Hash ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- Senhas ----------------
def get_password_hash(password: str) -> str:
    """
    Retorna o hash seguro de uma senha.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------------- Tokens JWT ----------------
def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """
    Cria um token JWT com payload e tempo de expiração.
    """
    to_encode = data.copy()
    if expires_delta is None:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodifica o token JWT e retorna o payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        raise ValueError(f"Token inválido: {str(e)}")
