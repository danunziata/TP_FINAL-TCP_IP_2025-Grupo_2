from pymodbus.client import ModbusTcpClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

MODBUS_HOST = "localhost"  # Reemplazar con la IP del servidor Modbus
MODBUS_PORT = 5020

# Configuración de InfluxDB
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "9b87FS8_-PvJYOYfVlU5-7MF6Oes9jhgFWitRcZp7-efOsaI3tMLoshBGdAQM_m-akDeE7fd1IoRNl8-aOzQwg=="  # Reemplazar con tu token
INFLUXDB_ORG = "Fila3"  # Reemplazar con tu organización
INFLUXDB_BUCKET = "Fila3"

# Input Registers (30001 → offset 0)
input_registers = [
    ("Ia", 0), ("Ib", 1), ("Ic", 2),
    ("Ua", 4), ("Ub", 5), ("Uc", 6),
    ("Ur", 7), ("Us", 8), ("Ut", 9),
    ("Uab", 10), ("Ubc", 11), ("Uca", 12),
    ("Urs", 13), ("Ust", 14), ("Utr", 15),
    ("KVA_A", 16), ("KVA_B", 17), ("KVA_C", 18),
    ("KW_A", 19), ("KW_B", 20), ("KW_C", 21),
    ("KVAr_A", 22), ("KVAr_B", 23), ("KVAr_C", 24),
    ("KVA_total", 25), ("KVAr_total", 26), ("KW_total", 27),
    ("Freq_abc", 60), ("Freq_rst", 61),
    ("FP_total", 67), ("FP_A", 68), ("FP_B", 69), ("FP_C", 70),
]

# Discrete Inputs (1X = 10001 → offset 0)
discrete_inputs = [
    ("AR_initiated", 3), ("Closed_AR", 75), ("Open_EF1+", 43),
    ("Open_SEF+", 50), ("Open_UF", 55), ("Open_Local", 59),
    ("Alarm", 63), ("Malfunction", 100), ("Excessive_Too", 105),
    ("Excessive_Tcc", 106),
]

def guardar_en_influxdb(write_api, analogos, booleanos):
    point = Point("mediciones_recloser")
    
    for nombre, valor in analogos.items():
        if nombre.startswith("Freq") or nombre.startswith("FP"):
            valor = valor / 100.0  # ajustar resolución
        point.field(nombre, valor)
    
    for nombre, estado in booleanos.items():
        point.field(nombre, int(estado))  # guardar bool como 0 o 1
    
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)

def main():
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    if not client.connect():
        print("No se pudo conectar al servidor Modbus.")
        return

    try:
        while True:
            analogos = {}
            booleanos = {}
            print("\n--- Consulta de registros ---")

            for nombre, offset in input_registers:
                result = client.read_input_registers(offset, count=1)
                if result.isError():
                    print(f"[ERROR] {nombre} (30000+{offset}): {result}")
                else:
                    valor = result.registers[0]
                    analogos[nombre] = valor
                    print(f"{nombre} = {valor}")

            for nombre, offset in discrete_inputs:
                result = client.read_discrete_inputs(offset, count=1)
                if result.isError():
                    print(f"[ERROR] {nombre} (10000+{offset}): {result}")
                else:
                    estado = result.bits[0]
                    booleanos[nombre] = estado
                    print(f"{nombre} = {'ON' if estado else 'OFF'}")

            guardar_en_influxdb(write_api, analogos, booleanos)
            print("Datos guardados en InfluxDB")
            time.sleep(15)

    except KeyboardInterrupt:
        print("Finalizando cliente Modbus.")
    finally:
        client.close()
        influx_client.close()

if __name__ == "__main__":
    main()

