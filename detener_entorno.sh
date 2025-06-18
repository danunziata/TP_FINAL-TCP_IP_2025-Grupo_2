#!/bin/bash

echo "🛑 Deteniendo todos los servicios de la simulación..."
echo "----------------------------------------------------"

# Detener los contenedores de Docker del servidor
echo "1. Deteniendo el servidor Modbus TCP..."
cd server_modbusTCP
docker-compose down
cd ..
echo "✅ Servidor detenido."
echo "----------------------------------------------------"

# Detener los contenedores de Docker de la base de datos
echo "2. Deteniendo la base de datos InfluxDB..."
cd database_InfluxDB
docker-compose down
cd ..
echo "✅ Base de datos detenida."
echo "----------------------------------------------------"

# Detener el proceso del cliente Python
echo "3. Deteniendo el cliente Python..."
# Busca y mata cualquier proceso llamado 'python3 client.py'
pkill -f "python3 client.py"
echo "✅ Cliente detenido."
echo "----------------------------------------------------"

echo "👍 Todos los servicios han sido detenidos."