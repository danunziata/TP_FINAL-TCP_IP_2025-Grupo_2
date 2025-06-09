from pymodbus.client import ModbusTcpClient
import time

MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020

# Lista de registros (nombre, offset)
registros = [
    ("Ia", 0), ("Ib", 1), ("Ic", 2),
    ("Ua", 4), ("Ub", 5), ("Uc", 6),
    ("Ur", 7), ("Us", 8), ("Ut", 9),
    ("KVA", 25), ("KVAr", 26), ("KW", 27)
]

def main():
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)

    if not client.connect():
        print("No se pudo conectar al servidor Modbus.")
        return

    try:
        while True:
            print("\n--- Consulta de registros ---")
            for nombre, offset in registros:
                result = client.read_input_registers(offset, count=1)
                if result.isError():
                    print(f"[ERROR] {nombre} (30000+{offset}): {result}")
                else:
                    print(f"{nombre} (30000+{offset}) = {result.registers[0]}")
            time.sleep(15)
    except KeyboardInterrupt:
        print("Finalizando cliente Modbus.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
