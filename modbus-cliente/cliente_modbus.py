from pymodbus.client import ModbusTcpClient
import psycopg2
from datetime import datetime
import time

client = ModbusTcpClient("osm27_ip", port=502)

conn = psycopg2.connect(
    host="timescaledb",
    port="5432",
    database="medicionesdb",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

while True:
    try:
        result = client.read_holding_registers(0, 10, unit=1)

        if not result.isError():
            values = (
                datetime.now(),
                result.registers[0] / 10.0,  # IA
                result.registers[1] / 10.0,  # IB
                result.registers[2] / 10.0,  # IC
                result.registers[3] / 10.0,  # VA
                result.registers[4] / 10.0,  # VB
                result.registers[5] / 10.0,  # VC
                result.registers[6],         # P_ACT
                result.registers[7],         # P_REACT
                result.registers[8] / 100.0, # FP
                result.registers[9]          # Estado
            )

            query = """
            INSERT INTO mediciones (fecha_hora, ia, ib, ic, va, vb, vc, p_act, p_react, fp, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, values)
            conn.commit()

            print(f"[OK] Medición insertada: {values}")

        else:
            print("[ERROR] Falló lectura Modbus")

    except Exception as e:
        print(f"[ERROR] {e}")

    time.sleep(5)

client.close()
cur.close()
conn.close()
