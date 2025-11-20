#app/crud/consultas
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models
from app.schemas import consultas

def criar_consulta(db: Session, consulta: consultas.ConsultaCreate, current_user: models.Usuario):
    paciente = db.query(models.Paciente).filter(models.Paciente.id == consulta.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    usuario_id = consulta.usuario_id or current_user.id
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verificar conflito de horário para o mesmo psicólogo
    conflito_usuario = db.query(models.Consulta).filter(
        models.Consulta.usuario_id == consulta.usuario_id,
        models.Consulta.data_hora == consulta.data_hora
    ).first()

    if conflito_usuario:
        raise HTTPException(
            status_code=400,
            detail="O psicólogo já possui uma consulta neste horário"
        )

    # Verificar conflito de horário para o mesmo paciente
    conflito_paciente = db.query(models.Consulta).filter(
        models.Consulta.paciente_id == consulta.paciente_id,
        models.Consulta.data_hora == consulta.data_hora
    ).first()

    if conflito_paciente:
        raise HTTPException(
            status_code=400,
            detail="O paciente já possui uma consulta neste horário"
        )

    db_consulta = models.Consulta(
        paciente_id=consulta.paciente_id,
        usuario_id=consulta.usuario_id,
        data_hora=consulta.data_hora,
        status=consulta.status
    )

    try:
        db.add(db_consulta)
        db.commit()
        db.refresh(db_consulta)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return db_consulta


def listar_consultas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Consulta).offset(skip).limit(limit).all()


def atualizar_consulta(db: Session, consulta_id: int, consulta_update: consultas.ConsultaUpdate):
    consulta = db.query(models.Consulta).filter(models.Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    # Pydantic V2: usa model_dump() em vez de dict()
    updates = consulta_update.model_dump(exclude_unset=True)

    # Atualiza apenas atributos existentes no modelo
    for key, value in updates.items():
        if hasattr(consulta, key):
            setattr(consulta, key, value)

    db.commit()
    db.refresh(consulta)
    return consulta


def delete_consulta(db: Session, consulta_id: int):
    consulta = db.query(models.Consulta).filter(models.Consulta.id == consulta_id).first()
    if consulta:
        db.delete(consulta)
        db.commit()
        return True
    return False
