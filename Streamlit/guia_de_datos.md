# 📊 Mapa de Registros para Simulación NOJA – Servidor Modbus

Este documento describe las direcciones utilizadas en la simulación de un recloser NOJA (modelo RC10/15/20). Los valores se generan aleatoriamente para pruebas y se organizan en registros tipo **Input Register (3X)** y **Discrete Input (1X)**.

> 🛑 **Importante**: en el script de simulación Python, los registros comienzan desde índice 0.  
> Por lo tanto:
> - El registro **30001** (NOJA) se accede como `context[0]`
> - El registro **10004** (NOJA) se accede como `context[3]`, etc.

---

## 📘 Input Registers (3X) – Datos analógicos

| Dirección NOJA | Índice Python  | Etiqueta            | Descripción                                     | Unidad / Escalado    |
|----------------|----------------|-------------------- |-------------------------------------------------|----------------------|
| 30001          | 0              | Ia                  | Corriente fase A                                | A (entero)           |
| 30002          | 1              | Ib                  | Corriente fase B                                | A (entero)           |
| 30003          | 2              | Ic                  | Corriente fase C                                | A (entero)           |
| 30005          | 4              | Ua                  | Tensión fase A - neutro                         | V                    |
| 30006          | 5              | Ub                  | Tensión fase B - neutro                         | V                    |
| 30007          | 6              | Uc                  | Tensión fase C - neutro                         | V                    |
| 30008–30010    | 7–9            | Uab, Ubc, Uca       | Tensión línea a línea entre fases               | V                    |
| 30011–30013    | 10–12          | Urs, Ust, Utr       | Tensión L-L entre secuencias RST                | V                    |
| 30014–30016    | 13–15          | Extra L-L (sim.)    | Tensiones adicionales (simuladas)               | V                    |
| 30017–30019    | 16–18          | kVA A/B/C           | Potencia aparente por fase                      | kVA                  |
| 30020–30022    | 19–21          | kW A/B/C            | Potencia activa por fase                        | kW                   |
| 30023–30025    | 22–24          | kVAr A/B/C          | Potencia reactiva por fase                      | kVAr                 |
| 30026          | 25             | kVA total           | Potencia aparente total                         | kVA                  |
| 30027          | 26             | kW total            | Potencia activa total                           | kW                   |
| 30028          | 27             | kVAr total          | Potencia reactiva total                         | kVAr                 |
| 30061          | 60             | Fabc                | Frecuencia lado ABC                             | Hz × 0.01            |
| 30062          | 61             | Frst                | Frecuencia lado RST                             | Hz × 0.01            |
| 30068          | 67             | PF 3ph              | Factor de potencia total                        | × 0.001              |
| 30069–30071    | 68–70          | PF A/B/C            | FP por fase A, B y C                            | × 0.001              |

---

## 📗 Discrete Inputs (1X) – Eventos simulados

| Dirección NOJA | Índice Python  | Evento Simulado      | Descripción (relación con NOJA)                      |
|----------------|----------------|----------------------|------------------------------------------------------|
| 10004          | 3              | AR initiated         | Se inició un ciclo de reconexión automática          |
| 10044          | 43             | Open (EF1+)          | Apertura por falla a tierra positiva                 |
| 10051          | 50             | Open (UF)            | Apertura por baja frecuencia                         |
| 10056          | 55             | Open (Local)         | Apertura manual o por panel                          |
| 10060          | 59             | Alarm                | Alarma de protección activa                          |
| 10064          | 63             | Malfunction          | Error general detectado en el recloser               |
| 10076          | 75             | Closed (AR)          | Cerrado por acción de reconexión automática (AR)     |
| 10101          | 100            | Excessive Too        | Tiempo de apertura excedido                          |
| 10106          | 105            | Excessive Tcc        | Tiempo de cierre excedido                            |
| 10107          | 106            | SIM Module Fault     | Falla en el módulo SIM                               |

---

## 🛠️ Notas

- Todos los valores se generan aleatoriamente con `random` en Python para simular lecturas realistas.
- Este mapeo es útil para conectar con herramientas como InfluxDB, Grafana o SCADA.
- Si estás usando un cliente Modbus que usa direcciones absolutas (como SCADA), usá directamente 30001, 10004, etc.
- Si estás usando índices en arrays (como en `pymodbus.context`), recordá aplicar **offset -1**.

---

## 📎 Referencias

- NOJA Power – Modbus User Guide (v2021)
- IEEE Std C37.239 – COMFEDE profile

