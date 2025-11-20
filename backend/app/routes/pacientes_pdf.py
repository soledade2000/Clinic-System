# app/routes/pacientes_pdf.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.crud import paciente as paciente_crud

router = APIRouter()

@router.get("/{paciente_id}/generate_pdf")
def gerar_pdf(paciente_id: int, db: Session = Depends(get_db)):
    paciente = paciente_crud.get_paciente(db, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # Diretório de saída
    out_dir = os.path.join("app", "uploads", "pdfs")
    os.makedirs(out_dir, exist_ok=True)

    filename = f"ficha_{paciente_id}_{paciente.nome_completo or 'paciente'}.pdf".replace(" ", "_")
    filepath = os.path.join(out_dir, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    x = 40
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Ficha de Cadastro - Projeto Mente e Corpo")

    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"Nome: {paciente.nome_completo or ''}")
    y -= 18
    c.drawString(x, y, f"Data de Nascimento: {paciente.data_nascimento or ''}")
    y -= 18
    c.drawString(x, y, f"Telefone: {paciente.telefone or ''}")
    y -= 18
    c.drawString(x, y, f"Endereço: {paciente.endereco or ''}")

    # Aqui você vai desenhar o restante do modelo da ficha (saúde, histórico etc)
    # conforme o PDF real
    # Exemplo:
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Histórico de Saúde")
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Queixa principal: {getattr(paciente, 'queixa', 'Não informada')}")

    c.showPage()
    c.save()

    return FileResponse(filepath, filename=filename, media_type="application/pdf")
