Instalar INFLUXDB en Ubuntu/Debian
1. Agregar la clave del repositorio
```bash
wget -qO- https://repos.influxdata.com/influxdata-archive_compat.key | sudo tee /etc/apt/keyrings/influxdata-archive_compat.key > /dev/null
```

2. Agregar el repositorio APT
```bash

echo 'deb [signed-by=/etc/apt/keyrings/influxdata-archive_compat.key] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
```
3. Actualizar e instalar
```bash
sudo apt update

sudo apt install influxdb2
```

4. Iniciar y habilitar el servicio
```bash

sudo systemctl enable influxdb
sudo systemctl start influxdb
```
5. Verificar que está corriendo
```bash
sudo systemctl status influxdb
```

6. Acceder a la interfaz de configuración

Abrí tu navegador en:

http://localhost:8086

Ahí vas a poder crear:

    Usuario admin

    Organización

    Bucket (base de datos)

    Token de acceso


Configurar InfluxDB:

- Abre http://localhost:8086 en tu navegador
- Crea una cuenta inicial
- Crea una organización (por ejemplo, "modbus_org")
- Crea un bucket llamado "modbus_data"
- Genera un token de API y guárdalo

Actualizar la configuración del cliente:

Edita el archivo client.py y actualiza las siguientes variables con tus valores:

- INFLUXDB_TOKEN
- INFLUXDB_ORG

Instalar las dependencias del cliente:
```bash
cd client_modbusTCP
pip install -r requirements.txt
```

Ejecutar el servidor:
```bash
cd server_modbusTCP
python server.py
```

Ejecutar el cliente (en otra terminal):
```bash
cd client_modbusTCP
python client.py
```
El sistema ahora:

- El servidor Modbus generará valores aleatorios cada 10 segundos
- El cliente leerá estos valores cada 15 segundos
- Los datos se guardarán automáticamente en InfluxDB
- Podrás visualizar los datos en el panel de control de InfluxDB en http://localhost:8086

Para visualizar los datos en InfluxDB:
- Ve a http://localhost:8086
En el menú lateral, selecciona "Data Explorer"
- Selecciona el bucket "modbus_data"

Puedes crear consultas para visualizar los datos, por ejemplo:
- Selecciona la medición "mediciones_recloser"
- Elige los campos que quieres visualizar (Ia, Ib, Ic, etc.)
- Configura el rango de tiempo
- Ejecuta la consulta

