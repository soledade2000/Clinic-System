# app/models/usuarios.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Enum as SqlEnum
from app.database import Base
from app.schemas.enums import CargoEnum 
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo: Mapped[CargoEnum] = mapped_column(SqlEnum(CargoEnum), default=CargoEnum.ADMIN, nullable=False)  
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    consultas = relationship("Consulta", back_populates="usuario")