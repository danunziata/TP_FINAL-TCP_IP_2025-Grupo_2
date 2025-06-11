from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, ModbusSequentialDataBlock
import logging
import random
import time
from threading import Thread

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

# Simular hasta el registro 30071 → offset 71
input_registers = [0] * 100

# Simular hasta el discrete input 10107 → offset 106
discrete_inputs = [False] * 110

store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, discrete_inputs),
    co=None,
    hr=None,
    ir=ModbusSequentialDataBlock(0, input_registers)
)
context = ModbusServerContext(slaves=store, single=True)

def update_registers(context):
    while True:
        values = {
            # Corrientes de línea
            0: random.randint(0, 100),
            1: random.randint(0, 100),
            2: random.randint(0, 100),
            # Voltajes fase-neutro
            4: random.randint(210, 240),
            5: random.randint(210, 240),
            6: random.randint(210, 240),
            # Voltajes fase-fase
            7: random.randint(360, 420),
            8: random.randint(360, 420),
            9: random.randint(360, 420),
            10: random.randint(360, 420),
            11: random.randint(360, 420),
            12: random.randint(360, 420),
            13: random.randint(360, 420),
            14: random.randint(360, 420),
            15: random.randint(360, 420),
            # Potencias por fase
            16: random.randint(0, 300),
            17: random.randint(0, 300),
            18: random.randint(0, 300),
            19: random.randint(0, 200),
            20: random.randint(0, 200),
            21: random.randint(0, 200),
            22: random.randint(0, 200),
            23: random.randint(0, 200),
            24: random.randint(0, 200),
            # Totales
            25: random.randint(0, 500),
            26: random.randint(0, 300),
            27: random.randint(0, 400),
            # Frecuencias (con resolución 0.01)
            60: random.randint(4900, 5100),  # 49.00 - 51.00 Hz
            61: random.randint(4900, 5100),
            # Factor de potencia (con resolución 0.001)
            67: random.randint(900, 1000),  # 0.900 - 1.000
            68: random.randint(800, 1000),
            69: random.randint(800, 1000),
            70: random.randint(800, 1000),
        }

        booleans = {
            3: random.choice([True, False]),
            43: random.choice([True, False]),
            50: random.choice([True, False]),
            55: random.choice([True, False]),
            59: random.choice([True, False]),
            63: random.choice([True, False]),
            75: random.choice([True, False]),
            100: random.choice([True, False]),
            105: random.choice([True, False]),
            106: random.choice([True, False]),
        }

        # Actualizar input registers
        for reg, val in values.items():
            context[0].setValues(4, reg, [val])

        # Actualizar discrete inputs
        for reg, val in booleans.items():
            context[0].setValues(2, reg, [val])

        log.info(f"Actualización de registros: {values} | Eventos: {booleans}")
        time.sleep(10)

def run_server():
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'SimuladorRecloser'
    identity.ProductCode = 'RC'
    identity.VendorUrl = 'http://example.com'
    identity.ProductName = 'Recloser Simulator'
    identity.ModelName = 'ModbusTCP'
    identity.MajorMinorRevision = '1.0'

    thread = Thread(target=update_registers, args=(context,))
    thread.daemon = True
    thread.start()

    StartTcpServer(context, identity=identity, address=("0.0.0.0", 5020))

if __name__ == "__main__":
    run_server()

# This code implements a Modbus TCP server that simulates a recloser device.
# It updates input registers with random values every 10 seconds.
# The server listens on port 5020 and can be accessed by Modbus clients.
# The server uses the pymodbus library to handle Modbus communication.
# The server runs in a separate thread to allow continuous updates while serving requests.
# The server's identity is set to provide information about the simulated device.