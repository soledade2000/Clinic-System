from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_hora = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="agendada")

    paciente = relationship("Paciente", back_populates="consultas")
    usuario = relationship("Usuario", back_populates="consultas")
