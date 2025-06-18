<!-- filepath: /home/sebalaborda/TP_FINAL-TCP_IP_2025-Grupo_2/Documentacion_TP_TCP_IP/docs/server_modbusTCP.md -->

# Documentación de la carpeta `server_modbusTCP`

Esta carpeta contiene un simulador de servidor Modbus TCP, utilizado para pruebas y desarrollo de sistemas de monitoreo eléctrico. El servidor simula variables analógicas y eventos, y expone los datos a través del protocolo Modbus TCP.

## Estructura de archivos

```
server_modbusTCP/
├── Dockerfile
├── README.md
├── docker-compose.yaml
├── requirements.txt
└── server.py
```

## Requisitos

- Docker
- Docker Compose


### 1. `Dockerfile`

El archivo `Dockerfile` define cómo construir la imagen Docker para el servidor Modbus TCP. Utiliza una imagen base de Python, instala las dependencias necesarias, copia los archivos del proyecto y expone el puerto 5020. Al iniciar el contenedor, ejecuta automáticamente el servidor Modbus TCP.

**¿Qué hace cada sección?**
- Usa la imagen oficial `python:3.11-slim` para asegurar un entorno ligero y compatible.
- Define `/app` como directorio de trabajo dentro del contenedor.
- Copia el archivo `requirements.txt` e instala las dependencias (en este caso, `pymodbus`).
- Copia el resto de los archivos del proyecto al contenedor.
- Expone el puerto 5020 para conexiones Modbus TCP.
- Define el comando por defecto para ejecutar el servidor (`python server.py`).

**Contenido del archivo:**

```dockerfile
# Usamos una imagen base oficial de Python
FROM python:3.11-slim

# Definimos directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todos los scripts al contenedor
COPY . .

EXPOSE 5020

# Definimos el comando por defecto (puedes cambiarlo luego)
CMD ["python", "server.py"]
```

---

### 2. `docker-compose.yaml`

El archivo `docker-compose.yaml` permite levantar el servidor Modbus TCP fácilmente usando Docker Compose. Define el servicio, el puerto expuesto y el nombre del contenedor.

**¿Qué hace cada sección?**
- Define el servicio `modbus-server` que se construye a partir del `Dockerfile`.
- Asigna un nombre fijo al contenedor.
- Expone el puerto 5020 del contenedor al host.
- Configura el reinicio automático del contenedor en caso de fallo.

**Contenido del archivo:**

```yaml
services:
  modbus-server:
    build: .
    container_name: modbus_server
    ports:
      - "5020:5020"
    restart: unless-stopped
```

---

### 3. `requirements.txt`

Este archivo lista las dependencias de Python necesarias para ejecutar el servidor. En este caso, solo se requiere la librería `pymodbus`.

**Contenido del archivo:**

```text
pymodbus
```

---

### 4. `server.py`

El script principal que implementa el servidor Modbus TCP simulado. Utiliza la librería `pymodbus` para crear el servidor, simula variables analógicas y eventos, y actualiza los valores periódicamente para pruebas y monitoreo.

**¿Qué hace cada sección?**
- Configura el servidor Modbus TCP y su identidad.
- Simula registros de entrada (input registers) y entradas discretas (discrete inputs).
- Actualiza periódicamente los valores de los registros con datos aleatorios para simular variables analógicas y eventos.
- Permite la conexión de clientes Modbus TCP para pruebas y monitoreo.

**Contenido del archivo:**

```python
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

# Inicializar estados booleanos persistentes
boolean_states = {
    3: False, 43: False, 50: False, 55: False, 59: False,
    63: False, 75: False, 100: False, 105: False, 106: False
}

def update_registers(context):
    change_prob = 0.025  # 10% de probabilidad de cambio

    while True:
        # Valores analógicos
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
            60: random.randint(4900, 5100),
            61: random.randint(4900, 5100),
            67: random.randint(900, 1000),
            68: random.randint(800, 1000),
            69: random.randint(800, 1000),
            70: random.randint(800, 1000),
        }

        # Actualizar input registers
        for reg, val in values.items():
            context[0].setValues(4, reg, [val])

        # Determinar si se produce un cambio esporádico en cada booleano
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
```

---

## Cómo iniciar el servidor

**Primera vez (construcción de imagen incluida):**

```bash
docker compose up --build
```

**Próximas veces:**

```bash
docker compose up
```

El servidor quedará disponible en `localhost:5020`.




