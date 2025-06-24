# Manual de Usuario

Universidad Nacional de Río Cuarto  
Ingeniería en Telecomunicaciones

![Logo UNRC](Aspose.Words.b496f225-9f91-474f-8df4-f7790ad34839.001.png)

**Manual de Usuario**

Sistema de monitoreo reconectador NOJA

**Fecha:** Junio 2025

Sistema de Monitoreo IPSEP / UNRC  
Manual de Usuario - Reconectador NOJA

![Imagen sistema](Aspose.Words.b496f225-9f91-474f-8df4-f7790ad34839.002.png)

---

## Índice

1. [Introducción](#introducción)
2. [Acceso al sistema](#acceso-al-sistema)
3. [Registro de usuario](#registro-de-usuario)
4. [Verificación por correo](#verificación-por-correo)
5. [Inicio de sesión](#inicio-de-sesión)
6. [Estructura general del sistema](#estructura-general-del-sistema)
7. [Variables disponibles](#variables-disponibles)
8. [Guía de uso paso a paso](#guía-de-uso-paso-a-paso)
9. [Consulta de eventos registrados](#consulta-de-eventos-registrados)

---

## Introducción

Este sistema fue desarrollado por estudiantes de la carrera de Ingeniería en Telecomunicaciones de la Universidad Nacional de Río Cuarto (UNRC), en colaboración con el IPSEP, con el objetivo de monitorear el comportamiento de un reconectador eléctrico marca NOJA. Permite visualizar en tiempo real tensiones, corrientes, potencias, frecuencia y eventos del sistema eléctrico.

---

## Acceso al sistema

### Registro de usuario

Desde la pantalla de inicio, el usuario debe completar los siguientes campos:

- Nombre y apellido
- Email válido
- Nombre de usuario
- Contraseña (mínimo 8 caracteres, con al menos un número y un símbolo especial)
- Confirmación de contraseña
- Captcha de seguridad

### Verificación por correo

Una vez enviado el formulario, se enviará un código de verificación al correo electrónico ingresado. Es necesario introducir dicho código para activar la cuenta.

### Inicio de sesión

Con la cuenta ya verificada, se puede acceder al sistema ingresando usuario y contraseña en la misma pantalla inicial.

---

## Estructura general del sistema

El sistema está dividido en varios módulos, cada uno con una función específica:

- Guía de uso e información de variables: proporciona instrucciones para utilizar la plataforma y una lista detallada de todas las variables disponibles, con su descripción y unidades.
- Gráfico de monitoreo en tiempo real: permite seleccionar una variable eléctrica y visualizar su comportamiento en tiempo real con actualización automática cada 15 segundos.
- Tabla de eventos registrados: muestra una lista de eventos detectados por el reconectador, como fallas, aperturas o cierres.
- Exportación de datos a CSV: permite filtrar variables por fecha y tipo, y exportar los resultados para su análisis externo o resguardo.

---

## Variables disponibles

**Tensiones (V):**
- Ua, Ub, Uc: tensiones de cada fase
- Uab, Ubc, Uca: tensiones entre líneas
- Urs, Ust, Utr: tensiones de referencia

**Corrientes (A):**
- Ia, Ib, Ic: corriente por fase

**Potencias:**
- KVA: Potencia aparente
- KW: Potencia activa
- KVAR: Potencia reactiva
- Por fase y total

**Frecuencia y Factor de Potencia:**
- Frecuencia ABC y RST
- FP: por fase y total

---

## Guía de uso paso a paso

### Importar datos

Use el botón correspondiente para cargar archivos CSV o Excel.

### Filtrar por fecha y hora

Seleccione un rango de fechas y horas para limitar los datos visualizados o exportados.

### Filtrar por tipo de variable

Elija entre tensiones, corrientes, potencias, etc., desde el selector correspondiente.

### Visualización de gráficos

- Seleccione categoría y variable específica.
- El gráfico se actualiza automáticamente cada 15 segundos.
- Se puede cambiar el intervalo temporal o pausar la actualización.
- Se muestran valores actuales, máximos, mínimos y promedio.

### Exportación de datos

- Filtre por fecha, hora y variable específica.
- Presione el botón Exportar CSV para descargar los datos filtrados.
- El archivo incluirá la fecha y hora como nombre de archivo.

---

## Consulta de eventos registrados

Permite visualizar eventos detectados por el reconectador, filtrando por fechas. Útil para diagnósticos y auditorías.

---
