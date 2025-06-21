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
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

# Deshabilitar el warning de MissingPivotFunction
warnings.simplefilter("ignore", MissingPivotFunction)

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
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_TOKEN = "9b87FS8_-PvJYOYfVlU5-7MF6Oes9jhgFWitRcZp7-efOsaI3tMLoshBGdAQM_m-akDeE7fd1IoRNl8-aOzQwg=="
INFLUXDB_ORG = "Fila3"
INFLUXDB_BUCKET = "Fila3"

# Cargar imagen de fondo como base64
with open("images/ipsep_photo.jpeg", "rb") as image_file:
    ipsep_bg_base64 = base64.b64encode(image_file.read()).decode()

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

# CSS para responsividad y layout
st.markdown(f"""
    <style>
        html, body, [data-testid="stAppViewContainer"] {{
            height: 100%;
            min-height: 100vh;
            background: linear-gradient(135deg, #6a89e6 0%, #8f6ed5 100%) !important;
            background-attachment: fixed !important;
        }}
        .main .block-container {{
            background: none !important;
        }}
        /* Glassmorphism para secciones y tarjetas */
        .section-container, .data-summary, div[data-testid="metric-container"], .streamlit-expanderHeader, .stDataFrame, .stTable {{
            background: rgba(255,255,255,0.18) !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18) !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }}
        /* Header principal con glassmorphism */
        .header-container {{
            background: rgba(106,137,230,0.85);
            border-radius: 24px;
            padding: 2.5rem 2rem 2rem 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.10);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .header-text h1 {{
            color: #fff;
            font-size: 2.7rem;
            font-weight: 800;
            text-shadow: 0 2px 8px rgba(0,0,0,0.18);
        }}
        .header-text p {{
            color: #f3f3f3;
            font-size: 1.2rem;
            font-weight: 400;
            text-shadow: 0 1px 4px rgba(0,0,0,0.12);
        }}
        /* Logos con fondo circular blanco y sombra */
        .logo-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 48px;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        .header-logo {{
            width: 170px;
            height: 170px;
            object-fit: contain;
            border-radius: 50%;
            background: #fff;
            box-shadow: 0 4px 24px 0 rgba(31, 38, 135, 0.18);
            padding: 16px;
            border: 2px solid #e0e0e0;
            transition: transform 0.3s;
        }}
        .header-logo:hover {{
            transform: scale(1.07);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.25);
        }}
        /* Glassmorphism para expanders y tablas */
        .streamlit-expanderHeader {{
            background: rgba(255,255,255,0.18) !important;
            border-radius: 14px !important;
            box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.10) !important;
            backdrop-filter: blur(6px) !important;
            -webkit-backdrop-filter: blur(6px) !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
        }}
        /* Métricas y tarjetas */
        div[data-testid="metric-container"] {{
            background: rgba(255,255,255,0.22) !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.10) !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
        }}
        /* Textos claros y con sombra */
        h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stText, .stDataFrame, .stTable {{
            color: #fff !important;
            text-shadow: 0 1px 4px rgba(0,0,0,0.10);
        }}
        /* Inputs y selectores */
        .stSelectbox > div > div, .stDateInput > div > div, .stTimeInput > div > div {{
            background: rgba(255,255,255,0.22) !important;
            border-radius: 12px !important;
            border: 1.5px solid rgba(255,255,255,0.25) !important;
            color: #222 !important;
        }}
        /* Botones */
        .stButton > button {{
            background: linear-gradient(135deg, #6a89e6 0%, #8f6ed5 100%) !important;
            border: 2px solid #fff !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            color: #fff !important;
            box-shadow: 0 4px 16px rgba(106,137,230,0.18);
            transition: all 0.3s;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(106,137,230,0.25);
        }}
        /* Scrollbar personalizada */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, #6a89e6 0%, #8f6ed5 100%);
            border-radius: 4px;
        }}
        /* Responsividad */
        @media (max-width: 768px) {{
            .header-container {{
                padding: 1.2rem 0.5rem 1.2rem 0.5rem;
            }}
            .header-text h1 {{
                font-size: 1.5rem;
            }}
            .logo-container {{
                gap: 18px;
            }}
            .header-logo {{
                width: 110px;
                height: 110px;
                padding: 8px;
            }}
        }}
        .stMetric {{
            background: rgba(255,255,255,0.22) !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.10) !important;
            border: 1.5px solid rgba(255,255,255,0.18) !important;
            padding: 1.2rem 0.5rem 1.2rem 0.5rem !important;
            margin: 0.5rem 0.5rem 0.5rem 0.5rem !important;
            min-width: 160px;
            min-height: 90px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}

        /* Forzar el color del texto a blanco para los labels y valores */
        .stMetric label, .stMetric div[data-testid="metric-value"] {{
            color: #fff !important;
            text-shadow: 0 1px 4px rgba(0,0,0,0.10);
        }}

        /* Ajuste responsivo */
        @media (max-width: 768px) {{
            .stMetric {{
                min-width: 100px;
                min-height: 60px;
                padding: 0.7rem 0.2rem 0.7rem 0.2rem !important;
            }}
        }}

        .streamlit-expander, .stExpander {{
            background: rgba(255,255,255,0.22) !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.10) !important;
            border: 1.5px solid rgba(255,255,255,0.18) !important;
            margin-bottom: 0.5rem !important;
            margin-top: 0.5rem !important;
        }}

        .glass-card {{
            background: rgba(255,255,255,0.22) !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.10) !important;
            border: 1.5px solid rgba(255,255,255,0.18) !important;
            padding: 1.5rem 1.5rem 1.5rem 1.5rem !important;
            margin-bottom: 2rem !important;
            margin-top: 0.5rem !important;
        }}

        body, html, [data-testid="stAppViewContainer"] {{
            position: relative;
        }}
        .background-image-blur {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            background: url('data:image/jpeg;base64,{ipsep_bg_base64}') center center/cover no-repeat;
            opacity: 0.18;
            filter: blur(3px);
            pointer-events: none;
        }}
        .main .block-container, .glass-card, .section-container, .data-summary, .stMetric, .streamlit-expander, .stExpander {{
            position: relative;
            z-index: 1;
        }}

        /* Centrar y compactar formularios de login y registro */
        .stAuthForm, .stRegisterForm, .stForm, .stLoginForm {{
            max-width: 600px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-top: 6vh !important;
            margin-bottom: 6vh !important;
            background: rgba(255,255,255,0.18) !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18) !important;
            padding: 2.2rem 2.2rem 1.5rem 2.2rem !important;
            backdrop-filter: blur(6px) !important;
            -webkit-backdrop-filter: blur(6px) !important;
        }}

        /* Ajustar títulos de formularios */
        .stAuthForm h2, .stRegisterForm h2, .stForm h2, .stLoginForm h2 {{
            font-size: 2rem !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-bottom: 1.2rem !important;
        }}

        /* Ajuste responsivo */
        @media (max-width: 600px) {{
            .stAuthForm, .stRegisterForm, .stForm, .stLoginForm {{
                max-width: 98vw !important;
                padding: 1.1rem 0.5rem 1.1rem 0.5rem !important;
            }}
        }}

        /* --- Estilo definitivo para el formulario "Cambiar contraseña" en la sidebar --- */
        [data-testid="stSidebar"] [data-testid="stForm"] {{
            background: linear-gradient(135deg, #6a89e6 0%, #8f6ed5 100%) !important;
            border-radius: 18px !important;
            padding: 1.5rem !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }}

        /* Texto del encabezado (h3) y labels dentro del formulario */
        [data-testid="stSidebar"] [data-testid="stForm"] h3,
        [data-testid="stSidebar"] [data-testid="stForm"] label {{
            color: white !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
        }}

        /* Botón de submit dentro del formulario de la sidebar */
        [data-testid="stSidebar"] [data-testid="stForm"] button {{
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }}
        [data-testid="stSidebar"] [data-testid="stForm"] button:hover {{
            background-color: rgba(255, 255, 255, 0.3) !important;
        }}

    </style>
    <div class="background-image-blur"></div>
""", unsafe_allow_html=True)

# Lógica de inicio de sesión con streamlit-authenticator
def run_auth():
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        api_key=config.get('api_key')
    )

    # Título y logos centrados
    logo_unrc_bytes = open("images/logo_unrc.png", "rb").read()
    logo_unrc_base64 = base64.b64encode(logo_unrc_bytes).decode("utf-8")
    ipsep_logo_bytes = open("images/logo_ipsep.png", "rb").read()
    ipsep_logo_base64 = base64.b64encode(ipsep_logo_bytes).decode("utf-8")
    st.markdown('''
    <div class="header-container" style="display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 32px;">
        <div style="flex:1; display: flex; justify-content: flex-end;">
            <img src="data:image/png;base64,{logo_unrc_base64}" class="header-logo" alt="Logo UNRC">
        </div>
        <div class="header-text" style="flex:2; text-align: center;">
            <h1>Sistema de Monitoreo para Reconectador NOJA</h1>
            <p>Monitoreo en tiempo real de variables eléctricas y eventos del sistema</p>
        </div>
        <div style="flex:1; display: flex; justify-content: flex-start;">
            <img src="data:image/jpeg;base64,{ipsep_logo_base64}" class="header-logo" alt="Logo IPSEP">
        </div>
    </div>
    <style>
    .header-logo {{
        width: 220px !important;
        height: 220px !important;
        min-width: 120px;
        min-height: 120px;
        object-fit: contain;
        border-radius: 50%;
        background: #fff;
        box-shadow: 0 4px 24px 0 rgba(31, 38, 135, 0.18);
        padding: 18px;
        border: 2px solid #e0e0e0;
        transition: transform 0.3s;
    }}
    @media (max-width: 1100px) {{
        .header-logo {{
            width: 140px !important;
            height: 140px !important;
            padding: 10px;
        }}
    }}
    @media (max-width: 768px) {{
        .header-container {{
            flex-direction: column !important;
            gap: 12px !important;
        }}
        .header-logo {{
            width: 90px !important;
            height: 90px !important;
            padding: 6px;
        }}
        .header-text {{
            text-align: center !important;
        }}
    }}
    </style>
    '''.format(logo_unrc_base64=logo_unrc_base64, ipsep_logo_base64=ipsep_logo_base64), unsafe_allow_html=True)

    # Mostrar primero el login y el registro en columnas si no está autenticado
    if st.session_state.get("authentication_status"):
        st.markdown(
            f'''<div style="
                background: rgba(60, 220, 120, 0.92);
                border-radius: 22px;
                box-shadow: 0 12px 36px 0 rgba(0, 0, 0, 0.25);
                border: 2px solid rgba(60, 220, 120, 1);
                padding: 1.5rem 1.6rem;
                margin-bottom: 1.8rem;
                display: inline-block;
                color: #ffffff;
                font-weight: bold;
                font-size: 1.35rem;
                text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                text-align: center;
            ">
                ✅ Bienvenido/a {st.session_state["name"]}
            </div>''',
            unsafe_allow_html=True
        )
        authenticator.logout("Cerrar sesión", "sidebar")
        
        # Volver a comprobar el estado de la sesión DESPUÉS de mostrar el botón de logout.
        # Esto evita que el widget de reseteo de contraseña se ejecute durante el proceso de logout.
        if st.session_state.get("authentication_status"):
            try:
                if authenticator.reset_password(
                    st.session_state.get('username'),
                    "sidebar",
                    fields={'Form name': 'Cambiar contraseña',
                            'Current password': 'Contraseña actual',
                            'New password': 'Nueva contraseña',
                            'Repeat password': 'Repetir contraseña',
                            'Reset': 'Cambiar contraseña'}
                ):
                    with open('config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
                    st.success("Contraseña modificada correctamente")
            except Exception as e:
                st.error(e)    
        return
    
    # Recuperación de usuario o de contraseña    
    elif st.session_state.get("authentication_status") is None or st.session_state.get("authentication_status") is False:
        _, col_login, col_gap, col_register, _ = st.columns([0.5, 1.2, 0.08, 1.2, 0.5])
        
        with st.expander("¿Olvidaste tu contraseña o tu nombre de usuario?"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Recuperar contraseña")
                st.write("Si olvidaste tu contraseña, ingresa tu usuario para recibir una nueva.")
                try:
                    username_of_forgotten_password, \
                    email_of_forgotten_password, \
                    new_random_password = authenticator.forgot_password(
                        send_email=True,
                        fields={'Form name': 'Olvidé mi contraseña',
                                'Username': 'Nombre de usuario',
                                'Submit': 'Recuperar contraseña'}
                        )
                    
                    if username_of_forgotten_password:
                        with open('config.yaml', 'w') as file:
                            yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
                        st.success('Nueva contraseña enviada a su correo electrónico.')

                    elif username_of_forgotten_password == False:
                        st.error('Usuario no encontrado')
                except Exception as e:
                    st.error(f"Error recuperando contraseña: {e}")

            with col2:
                st.subheader("Recuperar nombre de usuario")
                st.write("Si olvidaste tu nombre de usuario, ingresa tu correo electrónico.")
                try:
                    username_of_forgotten_username, \
                    email_of_forgotten_username = authenticator.forgot_username(
                        send_email=True,
                        fields={'Form name': 'Olvidé mi usuario',
                                'Submit': 'Recuperar usuario'}
                        )

                    if username_of_forgotten_username:
                        st.success('El nombre de usuario fue enviado a su correo electrónico.')
                    elif username_of_forgotten_username == False:
                        st.error('Email no encontrado')
                except Exception as e:
                    st.error(f"Error recuperando nombre de usuario: {e}")

                
        with col_login:
            login_status = authenticator.login(
                fields={'Form name': 'Inicio de sesión',
                        'Username': 'Usuario',
                        'Password': 'Contraseña',
                        'Login': 'Iniciar sesión'
                        },
            )
            if st.session_state.get("authentication_status") is False:
                st.markdown(
                    '''
                    <div style="background-color: #e63946; color: white; padding: 1rem 1.2rem; border-radius: 10px;
                                font-weight: bold; font-size: 1.05rem; margin-bottom: 1.2rem;
                                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); text-align: center;">
                        Usuario o contraseña incorrectos
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

        with col_register:
            try:
                email, username, name = authenticator.register_user(
                    two_factor_auth=True,
                    fields={'Form name': 'Registro de usuario',
                            'First name': 'Nombre',
                            'Last name': 'Apellido',
                            'Email': 'Email',
                            'Username': 'Nombre de usuario',
                            'Password': 'Contraseña',
                            'Repeat password': 'Repetir contraseña',
                            'Register': 'Registrarse'
                            },
                    password_hint=False
                    )
                if email:
                    st.success("Registro exitoso. Ahora puedes iniciar sesión.")
                    with open('config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)

            except Exception as e:
                error_msg = str(e).lower()

                if "email not valid" in error_msg:
                    st.markdown(
                        '''
                        <div style="background-color: #f94144; color: white; padding: 1rem 1.2rem; border-radius: 10px;
                                    font-weight: bold; font-size: 1.05rem; margin-bottom: 1.2rem;
                                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); text-align: center;">
                            ⚠️ Por favor, completa todos los campos del formulario.
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
                elif "password" in error_msg:
                    st.markdown(
                        '''
                        <div style="background-color: #f3722c; color: white; padding: 1.1rem 1.3rem; border-radius: 12px;
                                    font-weight: bold; font-size: 1rem; margin-bottom: 1.2rem;
                                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); text-align: left;">
                            🔐 La contraseña ingresada no cumple con los requisitos mínimos:<br><br>
                            • Entre 8 y 20 caracteres.<br>
                            • Al menos una letra <strong>minúscula</strong>.<br>
                            • Al menos una letra <strong>mayúscula</strong>.<br>
                            • Al menos un <strong>número</strong>.<br>
                            • Al menos un <strong>carácter especial</strong>: <code>!@#$%^&*()_+-=[]{};:'\"|,.&lt;&gt;/?`~</code>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
                else:
                    st.error(e)

        st.markdown('''
            <div style="width: 100%; text-align: center; margin-top: 48px; margin-bottom: 12px; color: #f3f3f3; font-size: 1.05rem; opacity: 0.85; letter-spacing: 0.02em;">
                © 2025 Grupo F3. Diseñado por Coassolo, Laborda, Lambrese, Magallanes, Milanesio, Novisardi, Tizzian. Todos los derechos reservados.
            </div>
        ''', unsafe_allow_html=True)
        st.stop()

# Agregar CSS para el contenedor flex de login y registro
st.markdown(f"""
<style>
.auth-flex-container {{
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: flex-start;
    gap: 48px;
    margin-top: 4vh;
    margin-bottom: 4vh;
    width: 100%;
    z-index: 2;
}}
.auth-flex-separator {{
    width: 32px;
    min-width: 32px;
    height: 1px;
    display: block;
}}
@media (max-width: 900px) {{
    .auth-flex-container {{
        flex-direction: column;
        align-items: center;
        gap: 24px;
    }}
    .auth-flex-separator {{
        width: 100%;
        min-width: 0;
        height: 24px;
    }}
}}
</style>
""", unsafe_allow_html=True)

run_auth()

# 1. First add the guides
st.header("📚 Documentación del Sistema")

col1, col2 = st.columns(2)

with col1:
    with st.expander("ℹ️ Guía de uso", expanded=True):
        st.markdown("""
        ### 🚀 Instrucciones de uso:
        
        **1. Importar datos** 
        - Use el botón '📥 Importar' para cargar archivos CSV o Excel.
        
        **2. Filtrar por fecha y hora** 
        - Seleccione el rango de fechas deseado
        - Puede especificar horas para un filtrado más preciso
        
        **3. Filtrar por tipo de datos** 
        - Use el selector para filtrar por tipo de variable (tensiones, corrientes, etc.)
        - Los datos mostrados se actualizarán automáticamente
        
        **4. Exportar datos** 
        - El botón 'Exportar CSV' descargará solo los datos filtrados actualmente visibles
        - El archivo incluirá la fecha y hora en su nombre para mejor organización
        
        **5. Visualización de gráficos**
        - Seleccione la categoría de variables que desea visualizar
        - Elija la variable específica para ver su comportamiento en el tiempo
        - Los gráficos se actualizan automáticamente cada 15 segundos
        """)

with col2:
    with st.expander("📊 Guía de datos", expanded=True):
        st.markdown("""
        ### ⚡ Variables disponibles:
        
        **🔌 Tensiones (V)**
        - **Fase (Ua, Ub, Uc)**: Tensiones de cada fase
        - **Referencia (Ur, Us, Ut)**: Tensiones de referencia
        - **Línea (Uab, Ubc, Uca)**: Tensiones entre líneas
        - **Referencia (Urs, Ust, Utr)**: Tensiones de referencia entre líneas
        - Valor nominal: **220V**
        
        **⚡ Corrientes (A)**
        - **Ia**: Corriente Fase A
        - **Ib**: Corriente Fase B
        - **Ic**: Corriente Fase C
        
        **🔋 Potencias**
        - **KVA**: Potencia Aparente (VA)
        - **KW**: Potencia Activa (W)
        - **KVAr**: Potencia Reactiva (VAR)
        - Disponible por fase (A, B, C) y total
        
        **📈 Frecuencia y Factor de Potencia**
        - **Freq_abc**: Frecuencia sistema ABC
        - **Freq_rst**: Frecuencia sistema RST
        - **FP**: Factor de Potencia (total y por fase)
        
        ### ⏰ Actualización de datos:
        - Frecuencia de actualización: **cada 15 segundos**
        - Rango de históricos: **últimas 24 horas**
        - Zona horaria: **Argentina (UTC-3)**
        
        ### 📋 Valores nominales:
        - Tensión de fase: **220V**
        - Frecuencia: **50Hz**
        - Factor de potencia ideal: **>0.95**
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
            'Frecuencias': {
                'variables': ['Freq_abc', 'Freq_rst'],
                'unidad': 'Hz',
                'color': '#663399',
                'titulo': 'Frecuencia'
            },
            'Factor de Potencia': {
                'variables': ['FP_total', 'FP_A', 'FP_B', 'FP_C'],
                'unidad': 'Adimensional',
                'color': '#663399',
                'titulo': 'Factor de Potencia'
            }
        }

        # Sección de gráficos
        st.header("📊 Gráfico de Monitoreo")
        st.markdown("<p style='margin-bottom: 2rem; color: #f3f3f3; font-size: 1.1rem;'>Visualización de variables en tiempo real con actualización automática</p>", unsafe_allow_html=True)

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

        # Botones de pausa/play y cambio de vista temporal DEBAJO de la gráfica
        if 'auto_refresh' not in st.session_state:
            st.session_state['auto_refresh'] = True
        if 'temporal_view_idx' not in st.session_state:
            st.session_state['temporal_view_idx'] = 0  # 0: 1h, 1d, 1w, Todo
        temporal_views = [
            ("1 hora", timedelta(hours=1)),
            ("1 día", timedelta(days=1)),
            ("1 semana", timedelta(weeks=1)),
            ("Todo", None)
        ]
        current_view, current_delta = temporal_views[st.session_state['temporal_view_idx']]

        # Filtrar datos para la gráfica según la vista temporal
        df_plot = df.copy()
        if current_delta is not None:
            max_time = df_plot['fecha_hora'].max()
            min_time = max_time - current_delta
            df_plot = df_plot[df_plot['fecha_hora'] >= min_time]

        # Crear gráfico
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_plot['fecha_hora'],
                y=df_plot[variable],
                name=variable,
                line=dict(
                    color=VARIABLES_CONFIG[categoria]['color'],
                    width=2
                )
            )
            )

        # Actualizar diseño
        fig.update_layout(
            title=dict(
                text=f"{VARIABLES_CONFIG[categoria]['titulo']} - {variable}",
                x=0,
                font=dict(size=16, color='#222')
            ),
            margin=dict(l=40, r=40, t=40, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            yaxis=dict(
                title=f"{VARIABLES_CONFIG[categoria]['titulo']} ({VARIABLES_CONFIG[categoria]['unidad']})",
                gridcolor='rgba(34,34,34,0.08)',  # gris claro
                zeroline=False,
                color='#222',
                titlefont=dict(color='#222'),
                tickfont=dict(color='#222')
            ),
            xaxis=dict(
                title="Tiempo",
                gridcolor='rgba(34,34,34,0.08)',  # gris claro
                zeroline=False,
                color='#222',
                titlefont=dict(color='#222'),
                tickfont=dict(color='#222')
            ),
            height=500,
            showlegend=False,
            hovermode='x unified',
            font=dict(color='#222')
        )

        # Mostrar la gráfica PRIMERO
        st.plotly_chart(fig, use_container_width=True)

        # Luego mostrar los botones DEBAJO de la gráfica
        col_pause, col_temporal, _ = st.columns([0.30, 0.50, 1.5])
        with col_pause:
            if st.session_state['auto_refresh']:
                if st.button('⏸️ Pausar actualización', key='pause_btn'):
                    st.session_state['auto_refresh'] = False
            else:
                if st.button('▶️ Reanudar actualización', key='resume_btn'):
                    st.session_state['auto_refresh'] = True
                    st.rerun()
        with col_temporal:
            if st.button(f'Cambiar vista temporal: {current_view}', key='temporal_btn'):
                st.session_state['temporal_view_idx'] = (st.session_state['temporal_view_idx'] + 1) % len(temporal_views)
                st.rerun()

        # Mostrar estadísticas básicas
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label=f"Valor actual",
                value=f"{df_plot[variable].iloc[-1]:.2f} {VARIABLES_CONFIG[categoria]['unidad']}"
            )

        with col2:
            st.metric(
                label=f"Promedio",
                value=f"{df_plot[variable].mean():.2f} {VARIABLES_CONFIG[categoria]['unidad']}"
            )

        with col3:
            st.metric(
                label=f"Máximo",
                value=f"{df_plot[variable].max():.2f} {VARIABLES_CONFIG[categoria]['unidad']}"
            )

        with col4:
            st.metric(
                label=f"Mínimo",
                value=f"{df_plot[variable].min():.2f} {VARIABLES_CONFIG[categoria]['unidad']}"
            )
            
        # Mostrar tabla de eventos
        st.header("📋 Filtro de eventos por fecha")

        col1_eventos, col2_eventos = st.columns(2)
        with col1_eventos:
            fecha_inicio_eventos = st.date_input("Fecha inicial eventos", value=datetime.now().date() - timedelta(days=7))
        with col2_eventos:
            fecha_fin_eventos = st.date_input("Fecha final eventos", value=datetime.now().date())
        # Convertir a datetime completos para el rango
        fecha_inicio_dt = datetime.combine(fecha_inicio_eventos, datetime.min.time())
        fecha_fin_dt = datetime.combine(fecha_fin_eventos, datetime.max.time())
        load_eventos(fecha_inicio_dt, fecha_fin_dt)

        # Continuar con el resto del código (filtros de fecha, etc.)
        st.header("🔍 Filtro para exportación de variables")
        
        # Filtros de tipo de dato y variable
        col_tipo, col_variable = st.columns(2)
        
        with col_tipo:
            tipo_dato = st.selectbox(
                "Tipo de dato",
                options=['Todos', 'Tensiones', 'Corrientes', 'Potencias', 'Frecuencias', 'Factor de potencia'],
                help="Seleccione el tipo de datos que desea visualizar"
            )
            
        with col_variable:
            if tipo_dato == 'Tensiones':
                variables = ['Todas', 'Ua', 'Ub', 'Uc', 'Ur', 'Us', 'Ut', 'Uab', 'Ubc', 'Uca', 'Urs', 'Ust', 'Utr']
            elif tipo_dato == 'Corrientes':
                variables = ['Todas', 'Ia', 'Ib', 'Ic']
            elif tipo_dato == 'Potencias':
                variables = ['Todas', 'KVA_A', 'KVA_B', 'KVA_C', 'KW_A', 'KW_B', 'KW_C',
                            'KVAr_A', 'KVAr_B', 'KVAr_C', 'KVA_total', 'KVAr_total', 'KW_total']
            elif tipo_dato == 'Frecuencias':
                variables = ['Todas', 'Freq_abc', 'Freq_rst']
            elif tipo_dato == 'Factor de potencia':
                variables = ['Todas', 'FP_total', 'FP_A', 'FP_B', 'FP_C']
            else:
                variables = ['Todas']
            
            variable_especifica = st.selectbox(
                "Variable específica",
                options=variables,
                help="Seleccione la variable específica para exportar"
            )

        # Filtros de fecha y hora
        col_fi, col_hi, col_ff, col_hf = st.columns(4)
        
        with col_fi:
            fecha_inicio = st.date_input(
                "Fecha inicial",
                min_value=df['fecha_hora'].min().date(),
                max_value=df['fecha_hora'].max().date(),
                value=df['fecha_hora'].min().date()
            )
        
        with col_hi:
            hora_inicio = st.time_input('Hora inicial', value=datetime.min.time())
            
        with col_ff:
            fecha_fin = st.date_input(
                "Fecha final",
                min_value=df['fecha_hora'].min().date(),
                max_value=df['fecha_hora'].max().date(),
                value=df['fecha_hora'].max().date()
            )
            
        with col_hf:
            hora_fin = st.time_input('Hora final', value=datetime.max.time())

        # Filtrar DataFrame según selección
        df_filtered = filter_dataframe(df, fecha_inicio, hora_inicio, fecha_fin, hora_fin)
        
        # Mostrar información del filtrado
        if len(df_filtered) > 0:
            st.markdown(f"""
                <div class="data-summary">
                    <h6>📊 Resumen de datos filtrados</h6>
                    <p><strong>📅 Período:</strong> {df_filtered['fecha_hora'].min().strftime('%Y-%m-%d %H:%M:%S')} a {df_filtered['fecha_hora'].max().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>🔍 Tipo de datos:</strong> {tipo_dato}</p>
                    <p><strong>📈 Registros encontrados:</strong> {len(df_filtered)}</p>
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
            st.markdown('<div style="display: flex; justify-content: center; margin-top: 1.5rem; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Exportar datos filtrados (CSV)",
                data=csv,
                file_name=f'datos_osm27_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="Descarga los datos filtrados actuales en formato CSV"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # Mostrar datos
            st.dataframe(
                df_filtered.assign(fecha_hora=df_filtered['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M:%S')),
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            # Agregar el auto-refresh (15 segundos = 15000 ms)
            if st.session_state['auto_refresh']:
                count = st_autorefresh(interval=15000, key="fizzbuzzcounter")

# Pie de página
st.markdown('''
    <div style="width: 100%; text-align: center; margin-top: 48px; margin-bottom: 12px; color: #f3f3f3; font-size: 1.05rem; opacity: 0.85; letter-spacing: 0.02em;">
        © 2025 Grupo F3. Diseñado por Coassolo, Laborda, Lambrese, Magallanes, Milanesio, Novisardi, Tizzian. Todos los derechos reservados.
    </div>
''', unsafe_allow_html=True)