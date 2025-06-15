from pymodbus.client import ModbusTcpClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "9b87FS8_-PvJYOYfVlU5-7MF6Oes9jhgFWitRcZp7-efOsaI3tMLoshBGdAQM_m-akDeE7fd1IoRNl8-aOzQwg=="
INFLUXDB_ORG = "Fila3"
INFLUXDB_BUCKET = "Fila3"

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

# Mapeo de direcciones booleanas a nombres técnicos
discrete_inputs = {
    3: "AR initiated",
    43: "Open (EF1+)",
    50: "Open (UF)",
    55: "Open (Local)",
    59: "Alarm",
    63: "Malfunction",
    75: "Closed (AR)",
    100: "Excessive Too",
    105: "Excessive Tcc",
    106: "SIM Module Fault",
}

# Mapeo de direcciones a descripciones legibles
descripciones_eventos = {
    3: "Se inició un ciclo de reconexión automática",
    43: "Apertura por falla a tierra positiva",
    50: "Apertura por baja frecuencia",
    55: "Apertura manual o por panel",
    59: "Alarma de protección activa",
    63: "Error general detectado en el recloser",
    75: "Cerrado por acción de reconexión automática (AR)",
    100: "Tiempo de apertura excedido",
    105: "Tiempo de cierre excedido",
    106: "Falla en el módulo SIM",
}

def guardar_en_influxdb(write_api, analogos, eventos):
    point = Point("mediciones_recloser")

    # Campos analógicos
    for nombre, valor in analogos.items():
        if nombre.startswith("Freq") or nombre.startswith("FP"):
            valor = valor / 100.0
        point.field(nombre, valor)

    # Campo eventos como string
    if eventos:
        eventos_str = ", ".join(eventos)
        point.field("eventos", eventos_str)

    write_api.write(bucket=INFLUXDB_BUCKET, record=point)

def main():
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    if not client.connect():
        print("No se pudo conectar al servidor Modbus.")
        return

    estados_anteriores = {offset: None for offset in discrete_inputs}

    try:
        while True:
            analogos = {}
            eventos = []
            print("\n--- Consulta de registros ---")

            # Lectura de registros analógicos
            for nombre, offset in input_registers:
                result = client.read_input_registers(offset, count=1)
                if result.isError():
                    print(f"[ERROR] {nombre} (30000+{offset}): {result}")
                else:
                    valor = result.registers[0]
                    analogos[nombre] = valor
                    print(f"{nombre} = {valor}")

            # Lectura de eventos
            for offset, nombre_tecnico in discrete_inputs.items():
                result = client.read_discrete_inputs(offset, count=1)
                if result.isError():
                    print(f"[ERROR] {nombre_tecnico} (10000+{offset}): {result}")
                else:
                    estado = result.bits[0]
                    estado_anterior = estados_anteriores[offset]

                    if estado_anterior is None:
                        estados_anteriores[offset] = estado
                    elif estado != estado_anterior:
                        descripcion = descripciones_eventos.get(offset, nombre_tecnico)
                        eventos.append(descripcion)
                        estados_anteriores[offset] = estado

                    print(f"{nombre_tecnico} = {'ON' if estado else 'OFF'}")

            guardar_en_influxdb(write_api, analogos, eventos)
            if eventos:
                print(f"Eventos detectados y guardados: {', '.join(eventos)}")
            else:
                print("No hubo eventos nuevos.")

            time.sleep(15)

    except KeyboardInterrupt:
        print("Finalizando cliente Modbus.")
    finally:
        client.close()
        influx_client.close()

if __name__ == "__main__":
    main()
