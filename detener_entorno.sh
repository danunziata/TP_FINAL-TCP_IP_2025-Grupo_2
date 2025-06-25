#!/bin/bash

echo "🛑 Deteniendo todos los servicios de la simulación..."
echo "----------------------------------------------------"

# Detener los contenedores de Docker del servidor
echo "1. Deteniendo el servidor Modbus TCP..."
cd server_modbusTCP
docker compose down
cd ..
echo "✅ Servidor detenido."
echo "----------------------------------------------------"

# Detener los contenedores de Docker de la base de datos y la web
echo "2. Deteniendo la base de datos InfluxDB y la web Streamlit..."
docker compose down
echo "✅ Base de datos y web detenida."
echo "----------------------------------------------------"

# Paso 4: Monitoreo
echo "4. Deteniendo servicios de monitoreo de contenedores..."
cd monitoreo
docker compose down
cd ..
echo "✅ Servicios de monitoreo detenidos."
echo "----------------------------------------------------"

# Detener el proceso del cliente Python
echo "3. Deteniendo el cliente Python..."
# Mata cualquier proceso llamado 'client.py'
pkill -f client.py
echo "✅ Cliente detenido."
echo "----------------------------------------------------"
echo "👍 Todos los servicios han sido detenidos."