from pymodbus.client import ModbusTcpClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
from datetime import datetime

MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020

# Configuración de InfluxDB
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "tu-token-aqui"  # Reemplazar con tu token
INFLUXDB_ORG = "tu-org"  # Reemplazar con tu organización
INFLUXDB_BUCKET = "modbus_data"

# Lista de registros (nombre, offset)
registros = [
    ("Ia", 0), ("Ib", 1), ("Ic", 2),
    ("Ua", 4), ("Ub", 5), ("Uc", 6),
    ("Ur", 7), ("Us", 8), ("Ut", 9),
    ("KVA", 25), ("KVAr", 26), ("KW", 27)
]

def guardar_en_influxdb(write_api, mediciones):
    point = Point("mediciones_recloser")
    for nombre, valor in mediciones.items():
        point.field(nombre, valor)
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)

def main():
    # Inicializar cliente Modbus
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    
    # Inicializar cliente InfluxDB
    influx_client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    if not client.connect():
        print("No se pudo conectar al servidor Modbus.")
        return

    try:
        while True:
            print("\n--- Consulta de registros ---")
            mediciones = {}
            
            for nombre, offset in registros:
                result = client.read_input_registers(offset, count=1)
                if result.isError():
                    print(f"[ERROR] {nombre} (30000+{offset}): {result}")
                else:
                    valor = result.registers[0]
                    print(f"{nombre} (30000+{offset}) = {valor}")
                    mediciones[nombre] = valor
            
            # Guardar mediciones en InfluxDB
            guardar_en_influxdb(write_api, mediciones)
            print("Datos guardados en InfluxDB")
            
            time.sleep(15)
    except KeyboardInterrupt:
        print("Finalizando cliente Modbus.")
    finally:
        client.close()
        influx_client.close()

if __name__ == "__main__":
    main()
