import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from mitosheet.streamlit.v1 import spreadsheet
from mitosheet.streamlit.v1.spreadsheet import _get_mito_backend
from datetime import datetime, timedelta
import hmac
import json
import re
import os
import base64
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# 1. PRIMERO: Configuración de la página (debe ser lo primero)
st.set_page_config(
    page_title='Sistema de Monitoreo OSM27',
    page_icon=':electric_plug:',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# # 2. Configurar el auto-refresh
# count = st_autorefresh(interval=15000, key="datarefresh")

# 3. Resto de las importaciones y configuraciones
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "9b87FS8_-PvJYOYfVlU5-7MF6Oes9jhgFWitRcZp7-efOsaI3tMLoshBGdAQM_m-akDeE7fd1IoRNl8-aOzQwg=="
INFLUXDB_ORG = "Fila3"
INFLUXDB_BUCKET = "Fila3"



# Agregar después de las importaciones

def filter_dataframe(df, fecha_inicio, hora_inicio, fecha_fin, hora_fin):
    """
    Filtra el DataFrame por fecha y hora.
    Maneja las zonas horarias correctamente usando UTC.
    """
    # Crear timestamps UTC para comparación
    datetime_inicio = pd.Timestamp(datetime.combine(fecha_inicio, hora_inicio)).tz_localize('UTC')
    datetime_fin = pd.Timestamp(datetime.combine(fecha_fin, hora_fin)).tz_localize('UTC')
    
    # Filtrar el DataFrame
    mask = (df['fecha_hora'] >= datetime_inicio) & (df['fecha_hora'] <= datetime_fin)
    return df.loc[mask].copy()

# Agregar después de las configuraciones de InfluxDB
def load_data():
    """Carga datos desde InfluxDB sin caché para permitir actualizaciones en tiempo real"""
    try:
        client = influxdb_client.InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        
        query_api = client.query_api()
        query = '''
        from(bucket: "Fila3")
          |> range(start: 0)
          |> filter(fn: (r) => r["_measurement"] == "mediciones_recloser")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        df = query_api.query_data_frame(query)
        if len(df) == 0:
            return pd.DataFrame()
            
        # Convertir timestamps de UTC a America/Argentina/Cordoba
        df = df.rename(columns={'_time': 'fecha_hora'})
        df['fecha_hora'] = pd.to_datetime(df['fecha_hora']).dt.tz_convert('America/Argentina/Cordoba')
        
        # Eliminar columnas no deseadas
        columns_to_drop = ['result', 'table', '_start', '_stop', '_measurement']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

        # Eliminar la columna 'eventos' si existe
        if 'eventos' in df.columns:
            df = df.drop(columns=['eventos'])
        
        return df
    except Exception as e:
        st.error(f"Error al conectar con InfluxDB: {str(e)}")
        return pd.DataFrame()

def load_eventos(fecha_inicio=None, fecha_fin=None):
    """Carga la columna 'eventos' desde InfluxDB y la muestra en formato tabla en Streamlit, con filtro de fechas."""
    try:
        client = influxdb_client.InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        query_api = client.query_api()
        # Si no se pasan fechas, traer todo
        if fecha_inicio is None or fecha_fin is None:
            rango = '|> range(start: 0)'
        else:
            # Convertir fechas a string en formato RFC3339
            start = fecha_inicio.strftime('%Y-%m-%dT%H:%M:%SZ')
            end = fecha_fin.strftime('%Y-%m-%dT%H:%M:%SZ')
            rango = f'|> range(start: {start}, stop: {end})'
        query = f'''
        from(bucket: "Fila3")
          {rango}
          |> filter(fn: (r) => r["_measurement"] == "mediciones_recloser")
          |> filter(fn: (r) => r["_field"] == "eventos")
          |> keep(columns: ["_time", "_value"])
        '''
        df = query_api.query_data_frame(query)
        if len(df) == 0:
            st.info("No hay eventos registrados en el rango seleccionado.")
            return
        df = df.rename(columns={"_time": "fecha_hora", "_value": "evento"})
        df['fecha_hora'] = pd.to_datetime(df['fecha_hora']).dt.tz_convert('America/Argentina/Cordoba')
        st.subheader("Tabla de eventos registrados")
        st.dataframe(df[['fecha_hora', 'evento']], use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al consultar eventos: {str(e)}")

# Eliminamos toda la lógica de usuarios y autenticación

def filter_dataframe(df, fecha_inicio, hora_inicio, fecha_fin, hora_fin):
    """
    Filtra el DataFrame por fecha y hora.
    Maneja las zonas horarias correctamente usando UTC.
    """
    # Crear timestamps UTC para comparación
    datetime_inicio = pd.Timestamp(datetime.combine(fecha_inicio, hora_inicio)).tz_localize('UTC')
    datetime_fin = pd.Timestamp(datetime.combine(fecha_fin, hora_fin)).tz_localize('UTC')
    
    # Filtrar el DataFrame
    mask = (df['fecha_hora'] >= datetime_inicio) & (df['fecha_hora'] <= datetime_fin)
    return df.loc[mask].copy()

# Agregar después de las configuraciones de InfluxDB
def load_data():
    """Carga datos desde InfluxDB sin caché para permitir actualizaciones en tiempo real"""
    try:
        client = influxdb_client.InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        
        query_api = client.query_api()
        query = '''
        from(bucket: "Fila3")
          |> range(start: 0)
          |> filter(fn: (r) => r["_measurement"] == "mediciones_recloser")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        df = query_api.query_data_frame(query)
        if len(df) == 0:
            return pd.DataFrame()
            
        # Convertir timestamps de UTC a America/Argentina/Cordoba
        df = df.rename(columns={'_time': 'fecha_hora'})
        df['fecha_hora'] = pd.to_datetime(df['fecha_hora']).dt.tz_convert('America/Argentina/Cordoba')
        
        # Eliminar columnas no deseadas
        columns_to_drop = ['result', 'table', '_start', '_stop', '_measurement']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

        # Eliminar la columna 'eventos' si existe
        if 'eventos' in df.columns:
            df = df.drop(columns=['eventos'])
        
        return df
    except Exception as e:
        st.error(f"Error al conectar con InfluxDB: {str(e)}")
        return pd.DataFrame()

def load_eventos(fecha_inicio=None, fecha_fin=None):
    """Carga la columna 'eventos' desde InfluxDB y la muestra en formato tabla en Streamlit, con filtro de fechas."""
    try:
        client = influxdb_client.InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        query_api = client.query_api()
        # Si no se pasan fechas, traer todo
        if fecha_inicio is None or fecha_fin is None:
            rango = '|> range(start: 0)'
        else:
            # Convertir fechas a string en formato RFC3339
            start = fecha_inicio.strftime('%Y-%m-%dT%H:%M:%SZ')
            end = fecha_fin.strftime('%Y-%m-%dT%H:%M:%SZ')
            rango = f'|> range(start: {start}, stop: {end})'
        query = f'''
        from(bucket: "Fila3")
          {rango}
          |> filter(fn: (r) => r["_measurement"] == "mediciones_recloser")
          |> filter(fn: (r) => r["_field"] == "eventos")
          |> keep(columns: ["_time", "_value"])
        '''
        df = query_api.query_data_frame(query)
        if len(df) == 0:
            st.info("No hay eventos registrados en el rango seleccionado.")
            return
        df = df.rename(columns={"_time": "fecha_hora", "_value": "evento"})
        df['fecha_hora'] = pd.to_datetime(df['fecha_hora']).dt.tz_convert('America/Argentina/Cordoba')
        st.subheader("Tabla de eventos registrados")
        st.dataframe(df[['fecha_hora', 'evento']], use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al consultar eventos: {str(e)}")

# CSS para responsividad y layout
st.markdown("""
    <style>
        .block-container {
            padding: 1rem;
        }
        .header-container {
            display: flex;
            align-items: center;
            gap: 2rem;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .header-logo {
            flex-shrink: 0;
            width: 120px;
            height: auto;
        }
        .header-text {
            flex-grow: 1;
        }
        .header-text h1 {
            margin: 0;
            font-size: 2rem;
            color: #1e1e1e;
        }
        .header-text p {
            margin: 0.5rem 0 0 0;
            color: #4a4a4a;
        }
        div[data-testid="metric-container"] {
            background-color: rgba(28, 131, 225, 0.1);
            border: 1px solid rgba(28, 131, 225, 0.1);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        @media (max-width: 768px) {
            .block-container {
                padding: 0.5rem;
            }
            .header-container {
                flex-direction: column;
                text-align: center;
                gap: 1rem;
            }
            .header-text h1 {
                font-size: 1.5rem;
            }
            div[data-testid="metric-container"] {
                padding: 1rem;
            }
            .element-container {
                font-size: 0.8rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Lógica de inicio de sesión con streamlit-authenticator
def run_auth():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        api_key=config.get('api_key')
    )

    # Título y logos centrados
    logo_unrc_bytes = open("logo_unrc.png", "rb").read()
    logo_unrc_base64 = base64.b64encode(logo_unrc_bytes).decode("utf-8")
    ipsep_logo_bytes = open("ipsep_logo.jpeg", "rb").read()
    ipsep_logo_base64 = base64.b64encode(ipsep_logo_bytes).decode("utf-8")
    st.markdown('''
    <div style="text-align: center; margin-bottom: 32px;">
        <h2 style="margin-bottom: 18px;">Sistema de Monitoreo para Reconectador NOJA</h2>
        <div style="display: flex; justify-content: center; align-items: center; gap: 40px; margin-bottom: 24px;">
            <img src="data:image/png;base64,{logo_unrc_base64}" style="max-width: 180px;">
            <img src="data:image/jpeg;base64,{ipsep_logo_base64}" style="max-width: 180px;">
        </div>
    </div>
    '''.format(logo_unrc_base64=logo_unrc_base64, ipsep_logo_base64=ipsep_logo_base64), unsafe_allow_html=True)

    # Mostrar primero el login, luego el registro (si no está autenticado)
    login_status = authenticator.login()
    # Mostrar advertencia entre login y registro si corresponde
    if st.session_state.get("authentication_status") is None:
        st.warning("Por favor, introduce tus credenciales")
    if st.session_state.get("authentication_status"):
        st.success(f"Bienvenido/a {st.session_state['name']}")
        authenticator.logout("Cerrar sesión", "sidebar")
        return  # No mostrar registro si ya está autenticado

    # Si no está autenticado, mostrar registro debajo del login y advertencia
    try:
        email, username, name = authenticator.register_user(two_factor_auth=True)
        if email:
            st.success("Registro exitoso. Ahora puedes iniciar sesión.")
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)
    if st.session_state.get("authentication_status") is False:
        st.error("Usuario o contraseña incorrectos")
        st.stop()
    elif st.session_state.get("authentication_status") is None:
        st.stop()
        

# # Botón de logout en la barra lateral
    authenticator.logout("Cerrar sesión", "sidebar")

run_auth()

# 1. First add the guides
st.header("Documentación del Sistema")
col1, col2 = st.columns(2)

with col1:
    with st.expander("ℹ️ Guía de uso", expanded=True):
        st.markdown("""
        ### Instrucciones:
        1. **Importar datos**: Use el botón '📥 Importar' para cargar archivos CSV o Excel.
        2. **Filtrar por fecha y hora**: 
           - Seleccione el rango de fechas deseado
           - Puede especificar horas para un filtrado más preciso
        3. **Filtrar por tipo de datos**: 
           - Use el selector para filtrar por tipo de variable (tensiones, corrientes, etc.)
           - Los datos mostrados se actualizarán automáticamente
        4. **Exportar datos**: 
           - El botón 'Exportar CSV' descargará solo los datos filtrados actualmente visibles
           - El archivo incluirá la fecha y hora en su nombre para mejor organización
        5. **Visualización de gráficos**:
           - Seleccione la categoría de variables que desea visualizar
           - Elija la variable específica para ver su comportamiento en el tiempo
           - Los gráficos se actualizan automáticamente cada 15 segundos
        """)

with col2:
    with st.expander("📊 Guía de datos", expanded=True):
        st.markdown("""
        ### Variables disponibles:
        
        #### Tensiones (V)
        - **Fase (Ua, Ub, Uc)**: Tensiones de cada fase
        - **Referencia (Ur, Us, Ut)**: Tensiones de referencia
        - **Línea (Uab, Ubc, Uca)**: Tensiones entre líneas
        - **Referencia (Urs, Ust, Utr)**: Tensiones de referencia entre líneas
        - Valor nominal: 220V
        
        #### Corrientes (A)
        - **Ia**: Corriente Fase A
        - **Ib**: Corriente Fase B
        - **Ic**: Corriente Fase C
        
        #### Potencias
        - **KVA**: Potencia Aparente (VA)
        - **KW**: Potencia Activa (W)
        - **KVAr**: Potencia Reactiva (VAR)
        - Disponible por fase (A, B, C) y total
        
        #### Frecuencia y Factor de Potencia
        - **Freq_abc**: Frecuencia sistema ABC
        - **Freq_rst**: Frecuencia sistema RST
        - **FP**: Factor de Potencia (total y por fase)
        
        ### Actualización de datos:
        - Frecuencia de actualización: cada 15 segundos
        - Rango de históricos: últimas 24 horas
        - Zona horaria: Argentina (UTC-3)
        
        ### Valores nominales:
        - Tensión de fase: 220V
        - Frecuencia: 50Hz
        - Factor de potencia ideal: >0.95
        """)

## 2. Then load and display data
with st.spinner('Actualizando Reporte...'):
    df = load_data()
    
    if df.empty:
        st.error("No hay datos disponibles")
    else:
        # Definir las categorías y variables disponibles
        VARIABLES_CONFIG = {
            'Tensiones': {
                'variables': ['Ua', 'Ub', 'Uc', 'Ur', 'Us', 'Ut', 'Uab', 'Ubc', 'Uca', 'Urs', 'Ust', 'Utr'],
                'unidad': 'V',
                'color': '#0066CC',
                'nominal': 220,
                'titulo': 'Tensión'
            },
            'Corrientes': {
                'variables': ['Ia', 'Ib', 'Ic'],
                'unidad': 'A',
                'color': '#CC0000',
                'titulo': 'Corriente'
            },
            'Potencias': {
                'variables': ['KVA_A', 'KVA_B', 'KVA_C', 'KW_A', 'KW_B', 'KW_C',
                             'KVAr_A', 'KVAr_B', 'KVAr_C', 'KVA_total', 'KVAr_total', 'KW_total'],
                'unidad': 'W/VA/VAR',
                'color': '#006633',
                'titulo': 'Potencia'
            },
            'Frecuencia y FP': {
                'variables': ['Freq_abc', 'Freq_rst', 'FP_total', 'FP_A', 'FP_B', 'FP_C'],
                'unidad': 'Hz/%',
                'color': '#663399',
                'titulo': 'Frecuencia/Factor de Potencia'
            }
        }

        # Sección de gráficos
        st.markdown("""
            <h3 style='margin-bottom: 0'>Gráfico de Monitoreo</h3>
            <p style='margin-bottom: 2rem'>Visualización de variables en tiempo real</p>
        """, unsafe_allow_html=True)

        # Selectores para categoría y variable
        col1, col2 = st.columns(2)

        with col1:
            categoria = st.selectbox(
                'Categoría',
                options=list(VARIABLES_CONFIG.keys()),
                help='Seleccione la categoría de variables a visualizar'
            )

        with col2:
            variable = st.selectbox(
                'Variable',
                options=VARIABLES_CONFIG[categoria]['variables'],
                help='Seleccione la variable específica a graficar'
            )

        # Crear gráfico
        fig = go.Figure()

        # Agregar la línea de datos
        fig.add_trace(
            go.Scatter(
                x=df['fecha_hora'],
                y=df[variable],
                name=variable,
                line=dict(
                    color=VARIABLES_CONFIG[categoria]['color'],
                    width=2
                )
            )
        )

        # Agregar línea nominal si es tensión
        if categoria == 'Tensiones':
            fig.add_hline(
                y=VARIABLES_CONFIG[categoria]['nominal'],
                line_dash="dash",
                line_color="rgba(255,0,0,0.5)",
                annotation_text="Valor nominal"
            )

        # Actualizar diseño
        fig.update_layout(
            title=dict(
                text=f"{VARIABLES_CONFIG[categoria]['titulo']} - {variable}",
                x=0,
                font=dict(size=16)
            ),
            margin=dict(l=40, r=40, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgb(240,240,240)',
            yaxis=dict(
                title=f"{VARIABLES_CONFIG[categoria]['titulo']} ({VARIABLES_CONFIG[categoria]['unidad']})",
                gridcolor='white',
                zeroline=False
            ),
            xaxis=dict(
                title="Tiempo",
                gridcolor='white',
                zeroline=False
            ),
            height=500,
            showlegend=False,
            hovermode='x unified'
        )

        # Mostrar gráfico
        st.plotly_chart(fig, use_container_width=True)

        # Mostrar estadísticas básicas
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label=f"Valor actual",
                value=f"{df[variable].iloc[-1]:.2f} {VARIABLES_CONFIG[categoria]['unidad']}"
            )

        with col2:
            st.metric(
                label=f"Promedio",
                value=f"{df[variable].mean():.2f} {VARIABLES_CONFIG[categoria]['unidad']}"
            )

        with col3:
            st.metric(
                label=f"Máximo",
                value=f"{df[variable].max():.2f} {VARIABLES_CONFIG[categoria]['unidad']}"
            )

        with col4:
            st.metric(
                label=f"Mínimo",
                value=f"{df[variable].min():.2f} {VARIABLES_CONFIG[categoria]['unidad']}"
            )

        # Continuar con el resto del código (filtros de fecha, etc.)
        st.markdown("##### 📅 Selección de período")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fecha_inicio = st.date_input(
                "Fecha inicial",
                min_value=df['fecha_hora'].min().date(),
                max_value=df['fecha_hora'].max().date(),
                value=df['fecha_hora'].min().date()
            )
        
        with col2:
            hora_inicio = st.time_input('Hora inicial', value=datetime.min.time())
            
        with col3:
            fecha_fin = st.date_input(
                "Fecha final",
                min_value=df['fecha_hora'].min().date(),
                max_value=df['fecha_hora'].max().date(),
                value=df['fecha_hora'].max().date()
            )
            
        with col4:
            hora_fin = st.time_input('Hora final', value=datetime.max.time())

        # Tercera fila - Filtros de datos
        st.markdown("##### 🔍 Filtros de datos")
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_dato = st.selectbox(
                "Tipo de dato",
                options=['Todos', 'Tensiones', 'Corrientes', 'Potencias'],
                help="Seleccione el tipo de datos que desea visualizar"
            )
            
        with col2:
            if tipo_dato == 'Tensiones':
                variables = ['Todas', 'Ua', 'Ub', 'Uc', 'Ur', 'Us', 'Ut', 'Uab', 'Ubc', 'Uca', 'Urs', 'Ust', 'Utr']
            elif tipo_dato == 'Corrientes':
                variables = ['Todas', 'Ia', 'Ib', 'Ic']
            elif tipo_dato == 'Potencias':
                variables = ['Todas', 'KVA_A', 'KVA_B', 'KVA_C', 'KW_A', 'KW_B', 'KW_C',
                            'KVAr_A', 'KVAr_B', 'KVAr_C', 'KVA_total', 'KVAr_total', 'KW_total']
            else:
                variables = ['Todas']
            
            variable_especifica = st.selectbox(
                "Variable específica",
                options=variables,
                help="Seleccione la variable específica para exportar"
            )

        # Filtrar DataFrame según selección
        df_filtered = filter_dataframe(df, fecha_inicio, hora_inicio, fecha_fin, hora_fin)
        
        # Mostrar información del filtrado
        if len(df_filtered) > 0:
            st.markdown(f"""
                <div style='padding: 1rem; background-color: rgba(28, 131, 225, 0.1); border-radius: 5px; margin: 1rem 0;'>
                    <h6 style='margin: 0; color: #0066CC;'>Resumen de datos filtrados:</h6>
                    <p style='margin: 0.5rem 0 0 0;'>Período: {df_filtered['fecha_hora'].min().strftime('%Y-%m-%d %H:%M:%S')} a {df_filtered['fecha_hora'].max().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style='margin: 0.2rem 0 0 0;'>Tipo de datos: {tipo_dato}</p>
                    <p style='margin: 0.2rem 0 0 0;'>Registros encontrados: {len(df_filtered)}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Filtrar columnas según selección
            if tipo_dato != 'Todos':
                if variable_especifica != 'Todas':
                    df_filtered = df_filtered[['fecha_hora', variable_especifica]]
                else:
                    # Seleccionar todas las variables de la categoría
                    if tipo_dato == 'Tensiones':
                        columnas = ['fecha_hora'] + [v for v in variables if v != 'Todas']
                    elif tipo_dato == 'Corrientes':
                        columnas = ['fecha_hora'] + [v for v in variables if v != 'Todas']
                    else:  # Potencias
                        columnas = ['fecha_hora'] + [v for v in variables if v != 'Todas']
                    df_filtered = df_filtered[columnas]

            # Botón de exportación
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                csv = df_filtered.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📊 Exportar datos filtrados (CSV)",
                    data=csv,
                    file_name=f'datos_osm27_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                    help="Descarga los datos filtrados actuales en formato CSV"
                )

            # Mostrar datos
            st.dataframe(
                df_filtered.assign(fecha_hora=df_filtered['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M:%S')),
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            # Agregar el auto-refresh (15 segundos = 15000 ms)
            count = st_autorefresh(interval=15000, key="fizzbuzzcounter")

# Mostrar tabla de eventos
st.subheader("Filtrar eventos por fecha")
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Fecha inicial eventos", value=datetime.now().date() - timedelta(days=7))
with col2:
    fecha_fin = st.date_input("Fecha final eventos", value=datetime.now().date())
# Convertir a datetime completos para el rango
fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())
load_eventos(fecha_inicio_dt, fecha_fin_dt)