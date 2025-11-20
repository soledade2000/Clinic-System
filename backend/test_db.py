from sqlalchemy import create_engine

# mesma string que você colocou no projeto
DATABASE_URL = "postgresql+psycopg2://postgres:87417705@localhost:5432/mente_e_corpo"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("✅ Conectado com sucesso!", conn)
except Exception as e:
    print("❌ Erro na conexão:", e)
