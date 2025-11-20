# app/crud/paciente.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models
from app.schemas import pacientes
from datetime import date


def _calc_idade(dn: date) -> int: 
    if not dn:
        return None
    hoje = date.today()
    return hoje.year - dn.year - ((hoje.month, hoje.day) < (dn.month, dn.day))

def criar_paciente(db: Session, paciente: pacientes.PacienteCreate) -> models.Paciente:
    existing_patient = db.query(models.Paciente).filter(models.Paciente.cpf == paciente.cpf).first()
    if existing_patient:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Paciente com este CPF já cadastrado")

    db_patient = models.Paciente(
        nome_completo=paciente.nome_completo,
        nome_social=paciente.nome_social,
        data_nascimento=paciente.data_nascimento,
        cpf=paciente.cpf,
        dependente=paciente.dependente,
        nome_responsavel=paciente.nome_responsavel,
        data_nascimento_responsavel=paciente.data_nascimento_responsavel,
        endereco=paciente.endereco,
        email=paciente.email,
        telefone=paciente.telefone,
        escolaridade=getattr(paciente.escolaridade, "value", paciente.escolaridade),
        religiao=getattr(paciente.religiao, "value", paciente.religiao),
        estado_civil=getattr(paciente.estado_civil, "value", paciente.estado_civil),
        servicos=paciente.servicos,
        disponibilidade_dias=paciente.disponibilidade_dias,
        horario_atendimento=paciente.horario_atendimento,
        renda_familiar=paciente.renda_familiar,
        idade=_calc_idade(paciente.data_nascimento),
        idade_responsavel=_calc_idade(paciente.data_nascimento_responsavel) if paciente.data_nascimento_responsavel else None,
    )
    try:
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_patient

def get_paciente(db: Session, paciente_id: int):
    """Busca um paciente específico pelo ID"""
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

def listar_pacientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Paciente).offset(skip).limit(limit).all()

def atualizar_paciente(db: Session, paciente_id: int, paciente_update: pacientes.PacienteUpdate):
    paciente_obj = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if not paciente_obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    update_data = paciente_update.model_dump(exclude_unset=True) # Use model_dump() aqui

    for key, value in update_data.items(): # Itere sobre o dicionário já criado
        if key in {"escolaridade", "religiao", "estado_civil"} and hasattr(value, "value"):
            value = value.value
        setattr(paciente_obj, key, value)

    if "data_nascimento" in update_data:
        paciente_obj.idade = _calc_idade(paciente_obj.data_nascimento) # type: ignore
    if "data_nascimento_responsavel" in update_data:
        paciente_obj.idade_responsavel = _calc_idade(paciente_obj.data_nascimento_responsavel) if paciente_obj.data_nascimento_responsavel else None # type: ignore

    db.commit()
    db.refresh(paciente_obj)
    return paciente_obj

def delete_paciente(db: Session, paciente_id: int):
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if paciente:
        db.delete(paciente)
        db.commit()
        return True
    return False

