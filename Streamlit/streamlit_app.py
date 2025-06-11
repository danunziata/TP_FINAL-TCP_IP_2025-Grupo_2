import streamlit as st
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

# Configuración de InfluxDB
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "9b87FS8_-PvJYOYfVlU5-7MF6Oes9jhgFWitRcZp7-efOsaI3tMLoshBGdAQM_m-akDeE7fd1IoRNl8-aOzQwg=="
INFLUXDB_ORG = "Fila3"
INFLUXDB_BUCKET = "Fila3"

# Función para cargar usuarios
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {"capo": "1234"}  # Usuario por defecto

# Función para guardar usuarios
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Función para validar email universitario
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@ing\.unrc\.edu\.ar$'
    return bool(re.match(pattern, email))

# Función para verificar la contraseña
def check_password():
    """Returns `True` if the user had the correct password."""
    
    users = load_users()

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in users and \
           hmac.compare_digest(st.session_state["password"], users[st.session_state["username"]]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    def register_user():
        """Register a new user."""
        email = st.session_state["reg_email"]
        password = st.session_state["reg_password"]
        
        if not is_valid_email(email):
            st.error("Por favor usa un correo @ing.unrc.edu.ar válido")
            return
        
        users = load_users()
        if email in users:
            st.error("Este usuario ya está registrado")
            return
        
        users[email] = password
        save_users(users)
        st.success("¡Registro exitoso! Ahora puedes iniciar sesión")

    def show_login_page(show_error=False, is_first_time=True):
        """Muestra la página de login con diseño consistente"""
        if is_first_time:
            # CSS original para la primera vez
            st.markdown("""
                <style>
                    .stButton>button {
                        width: 100%;
                        background-color: #0066CC;
                        color: white;
                        border: none;
                        padding: 0.5rem;
                        margin-top: 1rem;
                        border-radius: 4px;
                    }
                    .stButton>button:hover {
                        background-color: #0052a3;
                    }
                    .stTextInput>div>div {
                        padding: 0.5rem;
                        border-radius: 4px;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Logo UNRC
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 2rem;">
                    <img src="data:image/png;base64,{base64.b64encode(open('Logo_unrc_horizontal2.png', 'rb').read()).decode()}" 
                         style="max-width: 300px; margin: auto;" alt="UNRC Logo">
                </div>
            """, unsafe_allow_html=True)

            # Columnas originales sin centrado adicional
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <h3 style='margin-bottom: 1.5rem; color: #1e1e1e;'>Iniciar Sesión</h3>
                """, unsafe_allow_html=True)
                st.text_input("Usuario", key="username", 
                            placeholder="Ingresa tu usuario")
                st.text_input("Contraseña", type="password", key="password", 
                            placeholder="Ingresa tu contraseña")
                st.button("Ingresar", on_click=password_entered)
                
            with col2:
                st.markdown("""
                    <h3 style='margin-bottom: 1.5rem; color: #1e1e1e;'>Registrarse</h3>
                """, unsafe_allow_html=True)
                st.text_input("Correo Institucional", key="reg_email", 
                            help="Usa tu correo @ing.unrc.edu.ar",
                            placeholder="usuario@ing.unrc.edu.ar")
                st.text_input("Contraseña", type="password", key="reg_password",
                            placeholder="Crea una contraseña")
                st.button("Registrar", on_click=register_user)
        else:
            # CSS para la pantalla de cierre de sesión
            st.markdown("""
                <style>
                    .main {
                        max-width: 100%;
                        padding: 0;
                    }
                    .login-container {
                        max-width: 1000px;
                        margin: 2rem auto;
                        padding: 2rem;
                        background-color: white;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .stButton>button {
                        width: 100%;
                        background-color: #0066CC;
                        color: white;
                        border: none;
                        padding: 0.5rem;
                        margin-top: 1rem;
                        border-radius: 4px;
                    }
                    .stButton>button:hover {
                        background-color: #0052a3;
                    }
                    .stTextInput>div>div {
                        padding: 0.5rem;
                        border-radius: 4px;
                    }
                    .error-text {
                        color: #B00020;
                        background-color: #FFE9E9;
                        padding: 0.75rem;
                        border-radius: 4px;
                        margin-top: 1rem;
                        font-size: 0.9rem;
                        border: 1px solid #FFB4B4;
                    }
                    [data-testid="stAppViewContainer"] {
                        background-color: #f0f2f6;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Contenedor centrado para cierre de sesión
            col1, col2, col3 = st.columns([1,3,1])
            
            with col2:
                # Logo UNRC
                st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <img src="data:image/png;base64,{base64.b64encode(open('Logo_unrc_horizontal2.png', 'rb').read()).decode()}" 
                             style="max-width: 300px; margin: auto;" alt="UNRC Logo">
                    </div>
                """, unsafe_allow_html=True)

                with st.container():
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                            <h3 style='margin-bottom: 1.5rem; color: #1e1e1e;'>Iniciar Sesión</h3>
                        """, unsafe_allow_html=True)
                        st.text_input("Usuario", key="username", 
                                    placeholder="Ingresa tu usuario")
                        st.text_input("Contraseña", type="password", key="password", 
                                    placeholder="Ingresa tu contraseña")
                        st.button("Ingresar", on_click=password_entered)
                        if show_error:
                            st.markdown("""
                                <div class="error-text">
                                    <span>😕 Usuario o contraseña incorrectos</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                    with col2:
                        st.markdown("""
                            <h3 style='margin-bottom: 1.5rem; color: #1e1e1e;'>Registrarse</h3>
                        """, unsafe_allow_html=True)
                        st.text_input("Correo Institucional", key="reg_email", 
                                    help="Usa tu correo @ing.unrc.edu.ar",
                                    placeholder="usuario@ing.unrc.edu.ar")
                        st.text_input("Contraseña", type="password", key="reg_password",
                                    placeholder="Crea una contraseña")
                        st.button("Registrar", on_click=register_user)

    # Primera ejecución o sesión cerrada
    if "password_correct" not in st.session_state:
        show_login_page(is_first_time=True)
        return False
    
    # Contraseña incorrecta
    elif not st.session_state["password_correct"]:
        show_login_page(show_error=True, is_first_time=False)
        return False
    else:
        # Contraseña correcta, continuar
        return True

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

# Verificar contraseña
if check_password():
    # Configuración de la página
    st.set_page_config(
        page_title='Sistema de Monitoreo OSM27',
        page_icon=':electric_plug:',
        layout='wide',
        initial_sidebar_state='collapsed'
    )
    
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

    # Header con mejor diseño
    header_html = f"""
        <div class="header-container">
            <img class="header-logo" src="data:image/jpeg;base64,{base64.b64encode(open('Logo_unrc_horizontal2.png', 'rb').read()).decode()}" alt="UNRC Logo">
            <div class="header-text">
                <h1>Sistema de Monitoreo OSM27 - IPSEP UNRC</h1>
                <p><strong>UNRC - Facultad de Ingeniería</strong></p>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Botón para cerrar sesión
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["password_correct"] = False
        st.rerun()

    ## Data
    with st.spinner('Actualizando Reporte...'):
        
        # Cargar datos
        @st.cache_data
        def load_data():
            try:
                client = influxdb_client.InfluxDBClient(
                    url=INFLUXDB_URL,
                    token=INFLUXDB_TOKEN,
                    org=INFLUXDB_ORG
                )
                
                query_api = client.query_api()
                query = '''
                from(bucket: "Fila3")
                  |> range(start: -24h)
                  |> filter(fn: (r) => r["_measurement"] == "mediciones_recloser")
                  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                '''
                
                df = query_api.query_data_frame(query)
                if len(df) == 0:
                    return pd.DataFrame()
                    
                # Renombrar columnas y mantener fecha_hora como datetime
                df = df.rename(columns={'_time': 'fecha_hora'})
                df['fecha_hora'] = pd.to_datetime(df['fecha_hora'], utc=True)
                
                # Eliminar las columnas que no queremos
                columns_to_drop = ['result', 'table', '_start', '_stop', '_measurement']
                df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
                
                return df
            except Exception as e:
                st.error(f"Error al conectar con InfluxDB: {str(e)}")
                return pd.DataFrame()
        
        df = load_data()
        
        # Selector de variables
        variable_options = {
            'Tensiones': ['Ua', 'Ub', 'Uc'],
            'Corrientes': ['Ia', 'Ib', 'Ic'],
            'Potencias': ['KW', 'KVAr', 'KVA']  # Cambiamos p_act, p_react por KW, KVAr
        }
        
        selected_var = st.selectbox('Elegir Variable a Visualizar', 
                                   list(variable_options.keys()), 
                                   help='Seleccionar qué variables mostrar en los gráficos')
        
        # Métricas en contenedor responsive
        st.markdown("""
            <style>
                div[data-testid="metric-container"] {
                    background-color: rgba(28, 131, 225, 0.1);
                    border: 1px solid rgba(28, 131, 225, 0.1);
                    padding: 1rem;
                    border-radius: 5px;
                    margin-bottom: 0.5rem;
                }
                div[data-testid="metric-container"] > div {
                    width: 100%;
                }
                div[data-testid="metric-container"] label {
                    white-space: wrap;
                }
            </style>
        """, unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns((1,1,1,1))

        if selected_var == 'Tensiones':
            valor_pico = max(df[['Ua', 'Ub', 'Uc']].max())
            valor_anterior = df[['Ua', 'Ub', 'Uc']].iloc[-2].max() if len(df) > 1 else 0
            unidad = "V"
        elif selected_var == 'Corrientes':
            valor_pico = max(df[['Ia', 'Ib', 'Ic']].max())
            valor_anterior = df[['Ia', 'Ib', 'Ic']].iloc[-2].max() if len(df) > 1 else 0
            unidad = "A"
        else:  # Potencias
            valor_pico = max(df[['KW']].max())
            valor_anterior = df[['KW']].iloc[-2].max() if len(df) > 1 else 0
            unidad = "W"

        m1.write('')
        m2.metric(label ='Total de eventos de reconexión',
                  value = "Próximamente", 
                  delta = '', 
                  delta_color = 'off')
        m3.metric(label ='Tiempo desde última reconexión',
                  value = "Próximamente", 
                  delta = '', 
                  delta_color = 'off')
        m4.metric(label = f'{selected_var} - Valor pico',
                  value = f"{valor_pico:.2f} {unidad}", 
                  delta = f'{(valor_pico - valor_anterior):.2f} {unidad} vs anterior', 
                  delta_color = 'inverse')
        m1.write('')
         
    # Container para gráficos
    st.markdown("""
        <h3 style='margin-bottom: 0'>Gráficos de Monitoreo</h3>
        <p style='margin-bottom: 2rem'>Visualización de variables en tiempo real</p>
    """, unsafe_allow_html=True)
    
    # Configuración de estilo industrial
    COLORS = {
        'Ua': '#0066CC',  # Azul corporativo
        'Ub': '#003366',  # Azul oscuro
        'Uc': '#0099FF',  # Azul claro
        'Ia': '#CC0000',  # Rojo corporativo
        'Ib': '#990000',  # Rojo oscuro
        'Ic': '#FF0000',  # Rojo claro
        'KW': '#006633',  # Verde corporativo
        'KVAr': '#009966',  # Verde claro
        'KVA': '#333333'  # Gris oscuro
    }
    
    PLOT_BGCOLOR = 'rgb(240,240,240)'  # Fondo gris claro profesional
    GRID_COLOR = 'white'
    PLOT_HEIGHT = 300  # Altura para cada gráfico individual
    
    # Contenedor para los gráficos
    with st.container():
        if selected_var == 'Tensiones':
            variables = ['Ua', 'Ub', 'Uc']
            titles = ['Tensión Fase A', 'Tensión Fase B', 'Tensión Fase C']
            
            for var, title in zip(variables, titles):
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=df['fecha_hora'],
                        y=df[var],
                        name=var.upper(),
                        line=dict(color=COLORS[var], width=2)
                    )
                )
                
                fig.add_hline(
                    y=220,
                    line_dash="dash",
                    line_color="rgba(255,0,0,0.5)",
                    annotation_text="Tensión nominal"
                )
                
                fig.update_layout(
                    title=dict(text=title, x=0, font=dict(size=16)),
                    margin=dict(l=40, r=40, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor=PLOT_BGCOLOR,
                    yaxis=dict(
                        title="Tensión (V)",
                        gridcolor=GRID_COLOR,
                        zeroline=False
                    ),
                    xaxis=dict(
                        title="Tiempo",
                        gridcolor=GRID_COLOR,
                        zeroline=False
                    ),
                    height=PLOT_HEIGHT,
                    showlegend=False,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
        elif selected_var == 'Corrientes':
            variables = ['Ia', 'Ib', 'Ic']
            titles = ['Corriente Fase A', 'Corriente Fase B', 'Corriente Fase C']
            
            for var, title in zip(variables, titles):
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=df['fecha_hora'],
                        y=df[var],
                        name=var.upper(),
                        line=dict(color=COLORS[var], width=2)
                    )
                )
                
                fig.update_layout(
                    title=dict(text=title, x=0, font=dict(size=16)),
                    margin=dict(l=40, r=40, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor=PLOT_BGCOLOR,
                    yaxis=dict(
                        title="Corriente (A)",
                        gridcolor=GRID_COLOR,
                        zeroline=False
                    ),
                    xaxis=dict(
                        title="Tiempo",
                        gridcolor=GRID_COLOR,
                        zeroline=False
                    ),
                    height=PLOT_HEIGHT,
                    showlegend=False,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
        else:  # Potencias
            # Potencia Activa
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df['fecha_hora'],
                    y=df['KW'],
                    name="Potencia Activa",
                    line=dict(color=COLORS['KW'], width=2)
                )
            )
            fig.update_layout(
                title=dict(text="Potencia Activa", x=0, font=dict(size=16)),
                margin=dict(l=40, r=40, t=40, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor=PLOT_BGCOLOR,
                yaxis=dict(
                    title="Potencia (W)",
                    gridcolor=GRID_COLOR,
                    zeroline=False
                ),
                xaxis=dict(
                    title="Tiempo",
                    gridcolor=GRID_COLOR,
                    zeroline=False
                ),
                height=PLOT_HEIGHT,
                showlegend=False,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Potencia Reactiva
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df['fecha_hora'],
                    y=df['KVAr'],  # Cambiado de p_react a KVAr
                    name="Potencia Reactiva",
                    line=dict(color=COLORS['KVAr'], width=2)  # Cambiado de p_react a KVAr
                )
            )
            fig.update_layout(
                title=dict(text="Potencia Reactiva", x=0, font=dict(size=16)),
                margin=dict(l=40, r=40, t=40, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor=PLOT_BGCOLOR,
                yaxis=dict(
                    title="Potencia (VAR)",
                    gridcolor=GRID_COLOR,
                    zeroline=False
                ),
                xaxis=dict(
                    title="Tiempo",
                    gridcolor=GRID_COLOR,
                    zeroline=False
                ),
                height=PLOT_HEIGHT,
                showlegend=False,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Factor de Potencia
            fig = go.Figure()
            fig.add_annotation(
                text="Factor de Potencia - Próximamente",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=dict(text="Factor de Potencia", x=0, font=dict(size=16)),
                margin=dict(l=40, r=40, t=40, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor=PLOT_BGCOLOR,
                height=PLOT_HEIGHT
            )
            st.plotly_chart(fig, use_container_width=True)
        
    # Sección de manejo de datos estilo Excel
    st.markdown("""
        <style>
        /* Estilo para la sección de datos */
        .excel-like {
            background: white;
            padding: 1rem;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Estilo para los botones */
        .excel-button {
            background-color: #0066CC;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            margin: 0 0.5rem;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .excel-button:hover {
            background-color: #0052a3;
        }
        
        /* Estilo para la tabla */
        .dataframe {
            border: 1px solid #ddd;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        .dataframe th {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        .dataframe td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        
        .dataframe tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        /* Estilo para el área de búsqueda */
        .search-box {
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 1rem;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("Gestión de Datos")
    
    # Guía de uso
    with st.expander("ℹ️ Guía de uso"):
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
        """)

    # Contenedor principal
    with st.container():
        # Barra de herramientas - Primera fila
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader("📥 Importar", type=['csv', 'xlsx'])
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df_new = pd.read_csv(uploaded_file)
                    else:
                        df_new = pd.read_excel(uploaded_file)
                    st.success('Archivo importado correctamente')
                except Exception as e:
                    st.error(f'Error al importar: {str(e)}')
        
        # Segunda fila - Filtros de fecha y hora
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
                variables = ['Todas', 'Ua', 'Ub', 'Uc']
            elif tipo_dato == 'Corrientes':
                variables = ['Todas', 'Ia', 'Ib', 'Ic']
            elif tipo_dato == 'Potencias':
                variables = ['Todas', 'KW', 'KVAr', 'KVA']
            else:
                variables = ['Todas']
            
            variable_especifica = st.selectbox(
                "Variable específica",
                options=variables,
                help="Seleccione la variable específica a visualizar"
            )
    
    # Filtrar por fecha y hora
    df_filtered = filter_dataframe(df, fecha_inicio, hora_inicio, fecha_fin, hora_fin)
    
    # Filtrar por tipo de dato y variable específica
    if tipo_dato != 'Todos':
        if tipo_dato == 'Tensiones':
            columnas = ['fecha_hora', 'Ua', 'Ub', 'Uc']
            if variable_especifica != 'Todas':
                columnas = ['fecha_hora', variable_especifica]
        elif tipo_dato == 'Corrientes':
            columnas = ['fecha_hora', 'Ia', 'Ib', 'Ic']
            if variable_especifica != 'Todas':
                columnas = ['fecha_hora', variable_especifica]
        else:  # Potencias
            columnas = ['fecha_hora', 'KW', 'KVAr', 'KVA']
            if variable_especifica != 'Todas':
                columnas = ['fecha_hora', variable_especifica]
        
        df_filtered = df_filtered[columnas]
    # Información del filtrado
    st.markdown(f"""
        <div style='padding: 1rem; background-color: rgba(28, 131, 225, 0.1); border-radius: 5px; margin: 1rem 0;'>
            <h6 style='margin: 0; color: #0066CC;'>Resumen de datos filtrados:</h6>
            <p style='margin: 0.5rem 0 0 0;'>Período: {df_filtered['fecha_hora'].min().strftime('%Y-%m-%d %H:%M:%S')} UTC a {df_filtered['fecha_hora'].max().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p style='margin: 0.2rem 0 0 0;'>Tipo de datos: {tipo_dato} - Variable: {variable_especifica}</p>
            <p style='margin: 0.2rem 0 0 0;'>Registros encontrados: {len(df_filtered)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Botón de exportación con estilo mejorado
    st.markdown("""
        <style>
        div[data-testid="stDownloadButton"] button {
            background-color: #0066CC;
            color: white;
            font-weight: bold;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            width: 100%;
            transition: all 0.3s ease;
        }
        div[data-testid="stDownloadButton"] button:hover {
            background-color: #0052a3;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Contenedor para el botón de exportación
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        # Crear timestamps para el nombre del archivo
        export_inicio = datetime.combine(fecha_inicio, hora_inicio)
        export_fin = datetime.combine(fecha_fin, hora_fin)
        
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Exportar datos filtrados (CSV)",
            data=csv,
            file_name=f'datos_osm27_{export_inicio.strftime("%Y%m%d_%H%M")}_{export_fin.strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv',
            help="Descarga los datos filtrados actuales en formato CSV"
        )
    
    # Mostrar datos con estilo Excel
    st.dataframe(
        df_filtered.assign(fecha_hora=df_filtered['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M:%S')),
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Fin del programa
