FROM python:3.11-slim

# Dependências do sistema para psycopg2 e pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia requirements e instala (separado para cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copia todo o código do backend
COPY . /app

# Copia e dá permissão ao script de entrada
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expõe a porta do FastAPI
EXPOSE 8000

# Comando padrão do container
CMD ["/app/entrypoint.sh"]
