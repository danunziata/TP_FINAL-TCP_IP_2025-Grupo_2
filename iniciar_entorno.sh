#!/bin/bash

# Script para levantar todo el entorno de simulación Modbus, InfluxDB y Streamlit.

echo "🚀 Iniciando el proceso de despliegue completo..."
echo "----------------------------------------------------"

# Paso 1: Instalar requerimientos del cliente Python
echo "1. Instalando dependencias de Python..."
cd client_modbusTCP
pip install -r requirements.txt
cd ..
echo "✅ Dependencias instaladas."
echo "----------------------------------------------------"

# Paso 2: Levantar la base de datos InfluxDB y la web Streamlit con Docker compose
echo "2. Levantando la base de datos InfluxDB y web Streamlit con Docker Compose..."
docker compose up -d
echo "✅ Base de datos InfluxDB y web Streamlit iniciadas en segundo plano."
echo "----------------------------------------------------"

# Paso 3: Levantar el servidor Modbus TCP con Docker Compose
echo "3. Levantando el servidor Modbus TCP con Docker Compose..."
cd server_modbusTCP
docker compose up -d
cd ..
echo "✅ Servidor Modbus iniciado en segundo plano."
echo "----------------------------------------------------"

# Paso 4: Monitoreo
echo "3. Levantando servicios de monitoreo de contenedores..."
cd monitoreo
docker compose up -d
cd ..
echo "✅ Servicios de monitoreo iniciados."
echo "----------------------------------------------------"

# Pausa para dar tiempo a que los contenedores se inicien correctamente
echo "⏳ Esperando 10 segundos para que los servicios de Docker se estabilicen..."
sleep 10
echo "----------------------------------------------------"

# Paso 4: Iniciar el cliente Python para que empiece a enviar datos
echo "4. Iniciando el cliente Python (client.py) en segundo plano..."
cd client_modbusTCP
python3 client.py > /dev/null 2>&1 &
CLIENT_PID=$! # Captura el ID del proceso del cliente
cd ..
echo "✅ Cliente iniciado en segundo plano con PID: $CLIENT_PID."
echo "----------------------------------------------------"
echo "👍 Todos los servicios han sido iniciados."