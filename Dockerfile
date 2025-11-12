FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar aplicación
COPY src /app/src
WORKDIR /app/src

# Exponer puerto
EXPOSE 5000

# Usamos gunicorn para ejecutar la app (main:app)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"] 
