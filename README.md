# 🏥 Clinic System

O **Clinic System** é um sistema completo para gerenciamento de clínicas, oferecendo recursos para controle de pacientes, consultas, usuários, cargos e comunicação em tempo real.  
Foi desenvolvido para ser rápido, seguro, escalável e fácil de manter.

---

## 🚀 Tecnologias Utilizadas

### **Backend**
- Python
- FastAPI
- SQLAlchemy
- Alembic (migrações)
- PostgreSQL
- Docker & Docker Compose
- JWT para autenticação
- WebSockets

### **Frontend**
- (Caso exista) Next.js / React  
*(adicione aqui se você estiver usando)*

---

## 📂 Principais Funcionalidades

- Cadastro e gerenciamento de usuários  
- Sistema de cargos (admin, atendente, médico etc.)  
- Autenticação com JWT  
- CRUD de pacientes  
- Agendamento de consultas  
- Atualizações em tempo real via WebSockets  
- Banco de dados relacional com PostgreSQL  
- Migrações com Alembic  
- Estrutura organizada e modular

---

## 📦 Como Executar o Projeto

### 🔧 **Backend (FastAPI)**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
