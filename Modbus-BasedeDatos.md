1. Conectar con el dispositivo ModbusTCP

ModbusTCP es un protocolo que se comunica sobre TCP/IP. Puedes usar una biblioteca cliente de Modbus en tu lenguaje de programación preferido.
🔧 Bibliotecas comunes:

- Python: pymodbus

Ejemplo con Python (pymodbus):
```bash
from pymodbus.client.sync import ModbusTcpClient

client = ModbusTcpClient('192.168.0.100', port=502)
client.connect()

# Leer 2 registros holding a partir de la dirección 0
result = client.read_holding_registers(0, 2)
data = result.registers

client.close()
```
2. Elegir una base de datos

Depende de la aplicación:

- SQL (estructurado): PostgreSQL, MySQL, SQLite
- NoSQL (flexible): MongoDB, InfluxDB (ideal para datos de sensores)


3. Insertar los datos leídos

Una vez que lees los datos, simplemente los insertas en la base de datos.


Ejemplo insertando en PostgreSQL (usando psycopg2):

```bash
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="sensores",
    user="usuario",
    password="contraseña"
)
cursor = conn.cursor()

# Supón que data = [valor1, valor2]
cursor.execute("INSERT INTO lecturas (sensor1, sensor2) VALUES (%s, %s)", (data[0], data[1]))

conn.commit()
cursor.close()
conn.close()
```
 4. Automatizar con temporizador o ciclo

Puedes usar un bucle o schedule para leer e insertar datos periódicamente.

```bash
import time

while True:
    # Leer de Modbus
    result = client.read_holding_registers(0, 2)
    data = result.registers

    # Insertar en BD
    cursor.execute("INSERT INTO lecturas (sensor1, sensor2) VALUES (%s, %s)", (data[0], data[1]))
    conn.commit()

    time.sleep(5)  # Espera 5 segundos
```

EJEMPLO CON INFLUXDB (PARA MI EL QUE TENEMOS QUE UTILIZAR)

1. Instalar dependencias necesarias

```bash
pip install pymodbus influxdb-client
```
Paso 1: Leer datos desde ModbusTCP
```bash
from pymodbus.client.sync import ModbusTcpClient

# Configura la IP y puerto del dispositivo Modbus
client = ModbusTcpClient("192.168.0.100", port=502)
client.connect()

# Leer 2 registros holding desde la dirección 0
result = client.read_holding_registers(0, 2)
data = result.registers  # Por ejemplo: [25, 42]

client.close()
```

Paso 2: Insertar los datos en InfluxDB
```bash
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

# Configura tus credenciales y base de datos
url = "http://localhost:8086"
token = "TU_TOKEN"
org = "TU_ORG"
bucket = "modbus"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Crear un punto de datos
point = (
    Point("lectura_modbus")
    .tag("sensor", "plc1")
    .field("registro0", data[0])
    .field("registro1", data[1])
    .time(datetime.utcnow())
)

# Enviar a InfluxDB
write_api.write(bucket=bucket, org=org, record=point)
client.close()
```

Paso 3: Ejecutarlo en bucle

Si quieres hacer lecturas periódicas (ej. cada 10 segundos):

```bash
import time

while True:
    client = ModbusTcpClient("192.168.0.100", port=502)
    client.connect()

    result = client.read_holding_registers(0, 2)
    data = result.registers

    client.close()

    point = (
        Point("lectura_modbus")
        .tag("sensor", "plc1")
        .field("registro0", data[0])
        .field("registro1", data[1])
        .time(datetime.utcnow())
    )

    write_api.write(bucket=bucket, org=org, record=point)

    time.sleep(10)
```

Ver los datos en InfluxDB

Puedes consultar los datos desde:

    InfluxDB UI (http://localhost:8086)

    Usando Flux query como:

```bash
from(bucket: "modbus")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "lectura_modbus")
```

Notas importantes

    Si usas InfluxDB v1.x, cambia a la librería influxdb en lugar de influxdb-client.

    El valor del bucket debe estar creado previamente (o puedes crearlo desde la UI).

    Puedes añadir etiquetas (tag) como ID de dispositivo, zona, etc., para consultas más detalladas.