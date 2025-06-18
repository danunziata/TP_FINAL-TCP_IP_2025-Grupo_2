from pymodbus.client import ModbusTcpClient
import time

MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020

# Mapeo de registros con sus offsets
registros = {
    0: "Ia",
    1: "Ib",
    2: "Ic",
    4: "Ua",
    5: "Ub",
    6: "Uc",
    7: "Ur",
    8: "Us",
    9: "Ut",
    25: "KVA",
    26: "KVAr",
    27: "KW"
}

def main():
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)

    if not client.connect():
        print("No se pudo conectar al servidor Modbus.")
        return

    try:
        while True:
            # Leemos registros desde offset 0 hasta 27 (total 28 registros)
            result = client.read_input_registers(0, count=28)
            if result.isError():
                print(f"Error al leer registros: {result}")
            else:
                print("\n--- Valores leídos ---")
                for offset, nombre in registros.items():
                    valor = result.registers[offset]
                    print(f"{nombre} (30001 + {offset}) = {valor}")

            time.sleep(15)
    except KeyboardInterrupt:
        print("Finalizando cliente Modbus.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
