# Documentación de la carpeta `database_InfluxDB`

Esta carpeta contiene la configuración y los archivos necesarios para desplegar y utilizar una base de datos InfluxDB, tanto en forma local (instalación manual) como en contenedores Docker.

## Estructura de archivos

```
database_InfluxDB/
├── README.md
├── docker-compose.yaml
└── data/
    └── influxdb/
        ├── influxd.sqlite
        └── engine/
```

---

## 1. Instalación manual de InfluxDB en Ubuntu/Debian

Puedes instalar InfluxDB directamente en tu sistema operativo siguiendo estos pasos:

**Agregar la clave del repositorio:**
```bash
wget -qO- https://repos.influxdata.com/influxdata-archive_compat.key | sudo tee /etc/apt/keyrings/influxdata-archive_compat.key > /dev/null
```

**Agregar el repositorio APT:**
```bash
echo 'deb [signed-by=/etc/apt/keyrings/influxdata-archive_compat.key] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
```

**Actualizar e instalar InfluxDB:**
```bash
sudo apt update
sudo apt install influxdb2
```

**Iniciar y habilitar el servicio:**
```bash
sudo systemctl enable influxdb
sudo systemctl start influxdb
```

**Verificar que el servicio está corriendo:**
```bash
sudo systemctl status influxdb
```

**Acceder a la interfaz de configuración:**

Abre tu navegador en [http://localhost:8086](http://localhost:8086) y sigue los pasos para crear:
- Usuario admin
- Organización
- Bucket (base de datos)
- Token de acceso

---

## 2. `docker-compose.yaml`

Este archivo permite desplegar InfluxDB fácilmente usando Docker Compose. Define el servicio, el volumen persistente y las variables de entorno para la inicialización automática.

**¿Qué hace cada sección?**
- Usa la imagen oficial `influxdb:2.7`.
- Expone el puerto 8086 (web y API de InfluxDB).
- Monta un volumen persistente para los datos.
- Inicializa usuario, organización, bucket y token de admin automáticamente.

**Contenido del archivo:**

```yaml
services:
  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=Reconectador
      - DOCKER_INFLUXDB_INIT_PASSWORD=Capo1234
      - DOCKER_INFLUXDB_INIT_ORG=Fila3
      - DOCKER_INFLUXDB_INIT_BUCKET=Fila3
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=9b87FS8_-PvJYOYfVlU5-7MF6Oes9jhgFWitRcZp7-efOsaI3tMLoshBGdAQM_m-akDeE7fd1IoRNl8-aOzQwg==

volumes:
  influxdb_data:
    name: influxdb_data
```

---

## 3. Carpeta `data/influxdb/`

Esta carpeta almacena los datos persistentes de la base de datos InfluxDB cuando se utiliza Docker. No es necesario modificar su contenido manualmente.

- `influxd.sqlite`: Archivo principal de la base de datos.
- `engine/`: Carpeta interna utilizada por InfluxDB para el almacenamiento eficiente de datos.

---

## 4. Comandos para dejar InfluxDB funcionando

A continuación se muestran los comandos necesarios para levantar la base de datos InfluxDB usando Docker Compose y acceder a la interfaz web:

**Levantar el servicio por primera vez:**
```bash
docker compose up -d
```

**Ver logs del contenedor:**
```bash
docker compose logs -f
```

**Detener el servicio:**
```bash
docker compose down
```

**Acceder a la interfaz web:**

Abre tu navegador en:
```
http://localhost:8086
```

Desde ahí podrás gestionar la base de datos.

---


