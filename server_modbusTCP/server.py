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

# Reserva de 100 registros de entrada (input registers)
input_registers = [0] * 100

store = ModbusSlaveContext(
    di=None, co=None, hr=None,
    ir=ModbusSequentialDataBlock(0, input_registers)
)
context = ModbusServerContext(slaves=store, single=True)

def update_registers(context):
    while True:
        values = {
            0: random.randint(0, 100),
            1: random.randint(0, 100),
            2: random.randint(0, 100),
            4: random.randint(210, 240),
            5: random.randint(210, 240),
            6: random.randint(210, 240),
            7: random.randint(210, 240),
            8: random.randint(210, 240),
            9: random.randint(210, 240),
            25: random.randint(0, 500),
            26: random.randint(0, 300),
            27: random.randint(0, 400),
        }

        for reg, val in values.items():
            context[0].setValues(4, reg, [val])

        log.info(f"Actualización de registros: {values}")
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