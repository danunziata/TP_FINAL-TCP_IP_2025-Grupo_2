# **Informe de Requerimientos**

**Proyecto:** Sistema de Monitoreo para Reconectador Automático NOJA Power  
**Cliente:** IPSEP (Juan Carlos Amati)  
**Fecha:** 26/05  
**Equipo:** F3

---

## **1. Introducción**

Este informe documenta los requerimientos del sistema a desarrollar para el monitoreo de un reconectador automático **OSM27** de la marca **NOJA Power**, según lo relevado con el cliente. El objetivo es establecer los lineamientos funcionales y no funcionales para asegurar que el sistema cumpla con las necesidades operativas de monitoreo y análisis de datos eléctricos en tiempo real y de forma remota.

---

## **2. Descripción general**

El cliente requiere un sistema que permita **obtener, almacenar y visualizar** información crítica del reconectador automático, con el fin de realizar un monitoreo continuo del estado de la red eléctrica. La información debe ser accesible de forma remota desde una PC ubicada en las instalaciones del IPSEP, mediante conexión por cable Ethernet al dispositivo NOJA Power.

El sistema tomará mediciones cada **15 minutos** y guardará los datos preferentemente en un **archivo CSV**. Además, se solicitaron funcionalidades adicionales que mejoren la experiencia del usuario y la disponibilidad del sistema.

---

## **3. Requerimientos funcionales**

A continuación, se enumeran los requerimientos funcionales expresados por el cliente:

1. Obtener y registrar las siguientes variables eléctricas del reconectador:
   - Las tres tensiones.
   - Las tres corrientes.
   - Potencia activa.
   - Potencia reactiva.
   - Factor de potencia.
   - Eventos (reconexiones).

2. Guardar la información registrada en archivos CSV.

3. Registrar los datos con una periodicidad de **15 minutos**.

4. Permitir el acceso remoto al sistema desde una PC ubicada en el IPSEP.

5. Establecer la conexión con el reconectador NOJA Power mediante **cable Ethernet**.

---

## **4. Requerimientos no funcionales**

- El sistema debe estar disponible en todo momento (alta disponibilidad).
- La interfaz de usuario debe ser intuitiva y de fácil acceso.
- Se debe garantizar la integridad y seguridad de los datos registrados.

---

## **5. Requerimientos deseables**

Además de los requerimientos fundamentales, el cliente manifestó interés en que el sistema cuente con las siguientes características deseables:

- Acceso a una **versión gratuita** de la aplicación, compatible con dispositivos Android.
- Envío de **alertas por correo electrónico** ante eventos importantes.
- Visualización de **gráficas en función del tiempo**.
- Acceso a la plataforma desde **cualquier lugar**, facilitando el monitoreo remoto.
- Realizar una interfaz estilo **página web**.

---

## **6. Conclusión**

Este documento resume los requerimientos funcionales y no funcionales identificados durante el relevamiento con el cliente. Servirá como guía para la etapa de diseño e implementación del sistema. Una vez validado por el cliente, se considerará como base contractual del proyecto.
