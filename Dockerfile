FROM python:3.10.13-slim-bookworm

# Criar usuário não-root para executar a aplicação
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências de segurança e atualizar pacotes do sistema
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc libc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar apenas os requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copiar o projeto
COPY . .

# Mudar proprietário dos arquivos para o usuário não-root
RUN chown -R appuser:appuser /app

# Mudar para o usuário não-root
USER appuser

# Expor a porta que a aplicação usará
EXPOSE 5000

# Executar gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
