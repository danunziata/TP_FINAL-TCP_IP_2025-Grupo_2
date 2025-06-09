# Usamos una imagen base oficial de Python
FROM python:3.11-slim

# Definimos directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todos los scripts al contenedor
COPY . .

EXPOSE 5020

# Definimos el comando por defecto (puedes cambiarlo luego)
CMD ["python", "server.py"]

# Usar:
# docker build -t server_modbus .
# docker run --name server_modbus -p 5020:5020 server_modbus:latest