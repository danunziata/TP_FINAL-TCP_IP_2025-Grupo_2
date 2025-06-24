# Especificación de Requerimientos

Universidad Nacional de Río Cuarto  
Ingeniería en Telecomunicaciones

**Asignatura:** Aplicaciones TCP-IP  
**Fecha:** 25 de junio de 2025

![Imagen proyecto](Aspose.Words.e64cc4d2-ae6f-440a-a060-be1cda717d41.002.jpeg)

---

## Proyecto

**Sistema de Monitoreo para Reconectador Automático NOJA Power**  
**Cliente:** IPSEP (Juan Carlos Amati)

**Fecha de inicio de proyecto:** 19/05/2025  
**Fecha de entrega:** 25/06/2025  
**Equipo:** F3 - Grupo 2

---

## 1. Introducción

Este informe documenta los requerimientos del sistema a desarrollar para el monitoreo de un reconectador automático **OSM27** de la marca **NOJA Power**, según lo relevado con el cliente. El objetivo es establecer los lineamientos funcionales y no funcionales para asegurar que el sistema cumpla con las necesidades operativas de monitoreo y análisis de datos eléctricos en tiempo real y de forma remota.

---

## 2. Descripción general

El cliente requiere un sistema que permita **obtener, almacenar y visualizar** información crítica del reconectador automático, con el fin de realizar un monitoreo continuo del estado de la red eléctrica. La información debe ser accesible de forma remota a través de un sitio web.

---

## 3. Requerimientos funcionales

A continuación, se enumeran los requerimientos funcionales expresados por el cliente:

1. Obtención de las siguientes variables eléctricas del reconectador en función del tiempo:
   - Tensiones entre fase.
   - Tensiones entre fase y tierra.
   - Corrientes de fase a, b y c.
   - Potencia activa, reactiva y aparente de cada fase y total.
   - Factor de potencia de cada fase y total.
   - Frecuencia.
2. Registro de las variables con una periodicidad de 15 minutos.
3. Registro de cada evento ocurrido según el manual de usuario.
4. Provisión de una interfaz web accesible desde dentro de la red de la Universidad, a través de la cual los usuarios podrán consultar los requerimientos 1) y 3).
5. Exportación de los datos registrados en formato CSV, con el fin de que el cliente pueda analizarlos de forma independiente.
6. La interfaz deberá incluir un filtro para seleccionar un rango de fechas, de modo que se puedan exportar únicamente los datos correspondientes al período deseado.

---

## 4. Requerimientos no funcionales

1. Disponibilidad del sistema en todo momento, mediante su despliegue en un servidor de disponibilidad permanente, accesible a través de un dominio web registrado y operativo.
2. Implementación de un sistema de registro de usuarios y autenticación, permitiendo el acceso únicamente a personas autorizadas.

---

## 5. Requerimientos deseables

Además de los requerimientos fundamentales, el cliente manifestó interés en que el sistema cuente con las siguientes características deseables:

1. Envío de alertas por correo electrónico ante eventos importantes.
2. Autenticación por doble factor: registro de nuevos usuarios solicitando la confirmación de la dirección de correo electrónico.
3. Conservación de los datos registrados durante un período mínimo de un (1) año, permitiendo su consulta y exportación dentro de ese intervalo temporal.

---

## 6. Definición de datos

| Dato                           | Abreviatura | Tipo    | Unidad   | Resolución | Código  |
|--------------------------------|-------------|---------|----------|------------|---------|
| Corriente fase A               | Ia          | Entero  | Ampere   | 1 A        | 30001   |
| Corriente fase B               | Ib          | Entero  | Ampere   | 1 A        | 30002   |
| Corriente fase C               | Ic          | Entero  | Ampere   | 1 A        | 30003   |
| Tensión fase A - neutro        | Ua          | Entero  | Volt     | 1 V        | 30005   |
| Tensión fase B - neutro        | Ub          | Entero  | Volt     | 1 V        | 30006   |
| Tensión fase C - neutro        | Uc          | Entero  | Volt     | 1 V        | 30007   |
| Tensión entre R - neutro       | Ur          | Entero  | Volt     | 1 V        | 30008   |
| Tensión entre S - neutro       | Us          | Entero  | Volt     | 1 V        | 30009   |
| Tensión entre T - neutro       | Ut          | Entero  | Volt     | 1 V        | 30010   |
| Tensión entre líneas A y B     | Uab         | Entero  | Volt     | 1 V        | 30011   |
| Tensión entre líneas B y C     | Ubc         | Entero  | Volt     | 1 V        | 30012   |
| Tensión entre líneas C y A     | Uca         | Entero  | Volt     | 1 V        | 30013   |
| Tensión L-L entre secuencias RS| Urs         | Entero  | Volt     | 1 V        | 30014   |
| Tensión L-L entre secuencias ST| Ust         | Entero  | Volt     | 1 V        | 30015   |
| Tensión L-L entre secuencias TR| Utr         | Entero  | Volt     | 1 V        | 30016   |
| Potencia aparente fase A       | kVA A       | Entero  | kVA      | 1 kVA      | 30017   |
| Potencia aparente fase B       | kVA B       | Entero  | kVA      | 1 kVA      | 30018   |
| Potencia aparente fase C       | kVA C       | Entero  | kVA      | 1 kVA      | 30019   |
| Potencia activa fase A         | kW A        | Entero  | kW       | 1 kW       | 30020   |
| Potencia activa fase B         | kW B        | Entero  | kW       | 1 kW       | 30021   |
| Potencia activa fase C         | kW C        | Entero  | kW       | 1 kW       | 30022   |
| Potencia reactiva fase A       | kVAr A      | Entero  | kVAr     | 1 kVAr     | 30023   |
| Potencia reactiva fase B       | kVAr B      | Entero  | kVAr     | 1 kVAr     | 30024   |
| Potencia reactiva fase C       | kVAr C      | Entero  | kVAr     | 1 kVAr     | 30025   |
| Potencia aparente total        | kVA total   | Entero  | kVA      | 1 kVA      | 30026   |
| Potencia activa total          | kW total    | Entero  | kW       | 1 kW       | 30027   |
| Potencia reactiva total        | kVAr total  | Entero  | kVAr     | 1 kVAr     | 30028   |
| Frecuencia                     | Freq abc    | Decimal | Hz       | Hz * 0.01  | 30061   |
| Frecuencia lado RST            | Freq rst    | Decimal | Hz       | Hz * 0.01  | 30062   |
| Factor de potencia total       | Fp total    | Decimal | -        | *0.001     | 30068   |
| Factor de potencia fase A      | FP A        | Decimal | -        | *0.001     | 30069   |
| Factor de potencia fase B      | FP B        | Decimal | -        | *0.001     | 30070   |
| Factor de potencia fase C      | FP C        | Decimal | -        | *0.001     | 30071   |

---

## 7. Conclusión

Este documento resume los requerimientos funcionales y no funcionales identificados durante el relevamiento con el cliente. Servirá como guía para la etapa de diseño e implementación del sistema. Una vez validado por el cliente, se considerará como base contractual del proyecto.

© F3 2025, todos los derechos reservados.

[ref1]: Aspose.Words.e64cc4d2-ae6f-440a-a060-be1cda717d41.003.png
