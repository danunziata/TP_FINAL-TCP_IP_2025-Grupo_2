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

input_registers = [0] * 100
discrete_inputs = [False] * 110

store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, discrete_inputs),
    co=None,
    hr=None,
    ir=ModbusSequentialDataBlock(0, input_registers)
)
context = ModbusServerContext(slaves=store, single=True)

boolean_states = {
    3: False, 43: False, 50: False, 55: False, 59: False,
    63: False, 75: False, 100: False, 105: False, 106: False
}

def update_registers(context):
    change_prob = 0.025  # 2.5% de probabilidad de cambio

    while True:
        # Generar valores para registros con enteros "normales"
        values = {
            0: random.randint(0, 100),
            1: random.randint(0, 100),
            2: random.randint(0, 100),
            4: random.randint(210, 240),
            5: random.randint(210, 240),
            6: random.randint(210, 240),
            7: random.randint(360, 420),
            8: random.randint(360, 420),
            9: random.randint(360, 420),
            10: random.randint(360, 420),
            11: random.randint(360, 420),
            12: random.randint(360, 420),
            13: random.randint(360, 420),
            14: random.randint(360, 420),
            15: random.randint(360, 420),
            16: random.randint(0, 300),
            17: random.randint(0, 300),
            18: random.randint(0, 300),
            19: random.randint(0, 200),
            20: random.randint(0, 200),
            21: random.randint(0, 200),
            22: random.randint(0, 200),
            23: random.randint(0, 200),
            24: random.randint(0, 200),
            25: random.randint(0, 500),
            26: random.randint(0, 300),
            27: random.randint(0, 400),
        }

        # Registros 60 y 61 entre 49 y 51 con resolución 0.01 -> multiplicar por 100
        values[60] = int(random.uniform(49, 51) * 100)
        values[61] = int(random.uniform(49, 51) * 100)

        # Registros 67 a 70 entre 0 y 1 con resolución 0.001 -> multiplicar por 1000
        for reg in range(67, 71):
            values[reg] = int(random.uniform(0, 1) * 1000)

        # Actualizar input registers
        for reg, val in values.items():
            context[0].setValues(4, reg, [val])

        # Actualizar estados booleanos
        updated_booleans = {}
        for reg in boolean_states:
            if random.random() < change_prob:
                boolean_states[reg] = not boolean_states[reg]
            updated_booleans[reg] = boolean_states[reg]
            context[0].setValues(2, reg, [int(boolean_states[reg])])

        log.info(f"Actualización de registros: {values} | Eventos: {updated_booleans}")
        time.sleep(15)

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