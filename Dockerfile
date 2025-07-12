FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Configurar Python
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Instalar dependencias
RUN pip install --no-cache-dir gunicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Configurar entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]