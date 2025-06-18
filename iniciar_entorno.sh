#!/bin/bash

# Script para levantar todo el entorno de simulación Modbus, InfluxDB y Streamlit.

echo "🚀 Iniciando el proceso de despliegue completo..."
echo "----------------------------------------------------"

# Paso 1: Instalar requerimientos del cliente Python
echo "1. Instalando dependencias de Python desde requirements.txt..."
cd client_modbusTCP
pip install -r requirements.txt
cd ..
cd Streamlit
pip install -r requirements.txt
cd ..
echo "✅ Dependencias instaladas."
echo "----------------------------------------------------"

# Paso 2: Levantar el servidor Modbus TCP con Docker Compose
echo "2. Levantando el servidor Modbus TCP con Docker Compose..."
cd server_modbusTCP
docker compose up -d
cd ..
echo "✅ Servidor Modbus iniciado en segundo plano."
echo "----------------------------------------------------"

# Paso 3: Levantar la base de datos InfluxDB con Docker Compose
echo "3. Levantando la base de datos InfluxDB con Docker Compose..."
cd database_InfluxDB
docker compose up -d
cd ..
echo "✅ Base de datos InfluxDB iniciada en segundo plano."
echo "----------------------------------------------------"

# Pausa para dar tiempo a que los contenedores se inicien correctamente
echo "⏳ Esperando 10 segundos para que los servicios de Docker se estabilicen..."
sleep 10
echo "----------------------------------------------------"

# Paso 4: Iniciar el cliente Python para que empiece a enviar datos
echo "4. Iniciando el cliente Python (client.py) en segundo plano..."
cd client_modbusTCP
python3 client.py &
CLIENT_PID=$! # Captura el ID del proceso del cliente
cd ..
echo "✅ Cliente iniciado en segundo plano con PID: $CLIENT_PID."
echo "----------------------------------------------------"

# Paso 5: Iniciar la aplicación de visualización con Streamlit
echo "5. Iniciando la aplicación de visualización con Streamlit..."
cd Streamlit
streamlit run streamlit_app.py

# Mensaje final al cerrar Streamlit (con Ctrl+C)
echo "----------------------------------------------------"
echo "🛑 Aplicación Streamlit detenida."
echo "Para detener todos los servicios por completo, ejecuta el script 'detener_simulacion.sh' o los comandos de 'docker-compose down' en las carpetas correspondientes."