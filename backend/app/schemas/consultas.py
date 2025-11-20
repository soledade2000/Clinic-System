#app/schemas/consulta.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas import PacienteBase, UsuarioBase 

class ConsultaBase(BaseModel):
    data_hora: Optional[datetime] = None
    status: Optional[str] = "agendada"


class ConsultaCreate(ConsultaBase):
    paciente_id: int
    usuario_id: Optional[int] = None


class ConsultaUpdate(ConsultaBase):
    paciente_id: Optional[int] = None
    usuario_id: Optional[int] = None
    status: Optional[str] = None


class ConsultaOut(BaseModel):
    id: int
    data_hora: datetime
    status: str
    paciente: PacienteBase
    usuario: UsuarioBase

    model_config = ConfigDict(from_attributes=True)
