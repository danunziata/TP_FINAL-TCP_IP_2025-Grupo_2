# Dockerfile para app Streamlit
FROM python:3.12-slim

WORKDIR /app

# Copiar requirements y código
COPY requirements.txt ./
COPY streamlit_app.py ./
COPY config.yaml ./
COPY images/ ./images/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto por defecto de Streamlit
EXPOSE 8501

# Comando para ejecutar la app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
