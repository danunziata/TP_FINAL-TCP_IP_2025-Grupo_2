 Simulador de Recloser - Servidor Modbus TCP

Este proyecto implementa un **servidor Modbus TCP** simulado que actualiza registros de entrada con valores aleatorios cada 10 segundos. Utiliza la biblioteca `pymodbus` y escucha en el puerto `5020`.

## Estructura del proyecto

```
modbus_simulator/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── modbus_server.py
```

## Requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Cómo iniciar el servidor

### 🔨 Primera vez (construcción de imagen incluida)

```bash
docker compose up --build
```

Este comando:
- Construye la imagen desde el `Dockerfile`
- Instala las dependencias desde `requirements.txt`
- Inicia el contenedor y expone el puerto `5020`

### 🚀 Próximas veces (sin necesidad de reconstruir)

```bash
docker compose up
```

Este comando reutiliza la imagen previamente construida y simplemente inicia el servidor.

## Conexión

El servidor Modbus TCP queda disponible en:

```
Host: localhost
Puerto: 5020
```

Podés conectarte con un cliente Modbus como:
- [Modbus Poll (Windows)](https://modbustools.com/modbus_poll.html)
- [QModMaster (Linux/Windows)](https://sourceforge.net/projects/qmodmaster/)
- Script propio en Python usando `pymodbus.client`

---

## Detalles técnicos

- Se actualizan varios registros de entrada (`input registers`) con valores aleatorios entre 0–500 y 210–240 según el caso.
- El servidor se identifica como un dispositivo "Recloser Simulator".
- Se ejecuta de forma continua y no bloqueante gracias al uso de `threading`.

---