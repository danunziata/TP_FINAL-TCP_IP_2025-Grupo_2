# 🖥️ Sistema de Monitoreo para Reconectador NOJA en IPSEP

Este proyecto desarrolla un sistema de monitoreo remoto para un reconectador NOJA ubicado en el Instituto de Protecciones de Sistemas Eléctricos de Potencia (IPSEP).  
Utilizando el protocolo **Modbus TCP**, el sistema recopila métricas y registra eventos del equipo en tiempo real.  
Fue diseñado para facilitar al personal del IPSEP el acceso a esta información sin necesidad de desplazarse físicamente, presentando los datos a través de una **interfaz web amigable y accesible**.

---

## 👥 Integrantes

- Coassolo, Santiago  
- Laborda, Sebastián  
- Lambrese, Martín  
- Milanesio, Valentín  
- Novisardi, Maximiliano  
- Magallanes, Manuel  
- Tizzian, Ramiro  

---

## 🚀 Cómo levantar el sistema

### 1. Clonar el repositorio

```bash
git clone https://github.com/danunziata/TP_FINAL-TCP_IP_2025-Grupo_2.git
cd TP_FINAL-TCP_IP_2025-Grupo_2
```

### 2. Opciones para desplegar el sistema

#### Opción A: Instalar dependencias globalmente
Ejecutar directamente:

```bash
./iniciar_entorno.sh
```

#### Opción B: Usar entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
./iniciar_entorno.sh
```

---

## 🛑 Cómo detener el sistema

Para detener todos los servicios asociados:

```bash
./detener_entorno.sh
```

---

## 📄 Más información

Para una descripción completa del proyecto y utilización del sistema, acceda a la siguiente página:

🔗 [Documentación del Proyecto](https://danunziata.github.io/TP_FINAL-TCP_IP_2025-Grupo_2/)