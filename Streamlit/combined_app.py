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

    # Primera ejecución o sesión cerrada
    if "password_correct" not in st.session_state:
        # Crear dos columnas para login y registro
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Iniciar Sesión")
            st.text_input("Usuario", key="username")
            st.text_input("Contraseña", type="password", key="password")
            st.button("Ingresar", on_click=password_entered)
            
        with col2:
            st.subheader("Registrarse")
            st.text_input("Correo Institucional", key="reg_email", 
                         help="Usa tu correo @ing.unrc.edu.ar")
            st.text_input("Contraseña", type="password", key="reg_password")
            st.button("Registrar", on_click=register_user)
        
        return False
    
    # Contraseña incorrecta
    elif not st.session_state["password_correct"]:
        # Crear dos columnas para login y registro
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Iniciar Sesión")
            st.text_input("Usuario", key="username")
            st.text_input("Contraseña", type="password", key="password")
            st.button("Ingresar", on_click=password_entered)
            st.error("😕 Usuario o contraseña incorrectos")
            
        with col2:
            st.subheader("Registrarse")
            st.text_input("Correo Institucional", key="reg_email", 
                         help="Usa tu correo @ing.unrc.edu.ar")
            st.text_input("Contraseña", type="password", key="reg_password")
            st.button("Registrar", on_click=register_user)
        
        return False
    else:
        # Contraseña correcta, continuar
        return True

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
            <img class="header-logo" src="data:image/jpeg;base64,{base64.b64encode(open('unrc_logo.jpg', 'rb').read()).decode()}" alt="UNRC Logo">
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
            df = pd.read_csv('mediciones_exportadas.csv')
            df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
            return df
        
        df = load_data()
        
        # Selector de variables
        variable_options = {
            'Tensiones': ['va', 'vb', 'vc'],
            'Corrientes': ['ia', 'ib', 'ic'],
            'Potencias': ['p_act', 'p_react', 'fp']
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
        
        # Cálculo de métricas según la variable seleccionada
        total_reconexiones = len(df[df['estado'] == 1])
        tiempo_ultima = (datetime.now() - df[df['estado'] == 1]['fecha_hora'].max()).seconds // 60
        
        if selected_var == 'Tensiones':
            valor_pico = max(df[['va', 'vb', 'vc']].max())
            valor_anterior = df[['va', 'vb', 'vc']].iloc[-2].max()
            unidad = "V"
        elif selected_var == 'Corrientes':
            valor_pico = max(df[['ia', 'ib', 'ic']].max())
            valor_anterior = df[['ia', 'ib', 'ic']].iloc[-2].max()
            unidad = "A"
        else:  # Potencias
            valor_pico = max(df[['p_act']].max())
            valor_anterior = df[['p_act']].iloc[-2].max()
            unidad = "W"
        
        m1.write('')
        m2.metric(label ='Total de eventos de reconexión',
                  value = total_reconexiones, 
                  delta = 'Últimas 24 hs', 
                  delta_color = 'inverse')
        m3.metric(label ='Tiempo desde última reconexión',
                  value = f"{tiempo_ultima} mins", 
                  delta = 'Último evento registrado', 
                  delta_color = 'inverse')
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
        'va': '#0066CC',  # Azul corporativo
        'vb': '#003366',  # Azul oscuro
        'vc': '#0099FF',  # Azul claro
        'ia': '#CC0000',  # Rojo corporativo
        'ib': '#990000',  # Rojo oscuro
        'ic': '#FF0000',  # Rojo claro
        'p_act': '#006633',  # Verde corporativo
        'p_react': '#009966',  # Verde claro
        'fp': '#333333'  # Gris oscuro
    }
    
    PLOT_BGCOLOR = 'rgb(240,240,240)'  # Fondo gris claro profesional
    GRID_COLOR = 'white'
    PLOT_HEIGHT = 300  # Altura para cada gráfico individual
    
    # Contenedor para los gráficos
    with st.container():
        if selected_var == 'Tensiones':
            variables = ['va', 'vb', 'vc']
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
            variables = ['ia', 'ib', 'ic']
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
                    y=df['p_act'],
                    name="Potencia Activa",
                    line=dict(color=COLORS['p_act'], width=2)
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
                    y=df['p_react'],
                    name="Potencia Reactiva",
                    line=dict(color=COLORS['p_react'], width=2)
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
            fig.add_trace(
                go.Scatter(
                    x=df['fecha_hora'],
                    y=df['fp'],
                    name="Factor de Potencia",
                    line=dict(color=COLORS['fp'], width=2)
                )
            )
            fig.update_layout(
                title=dict(text="Factor de Potencia", x=0, font=dict(size=16)),
                margin=dict(l=40, r=40, t=40, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor=PLOT_BGCOLOR,
                yaxis=dict(
                    title="Factor de Potencia",
                    gridcolor=GRID_COLOR,
                    zeroline=False,
                    range=[0, 1]
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
        
    # Sección de Mito con responsive design
    st.markdown("""
        <style>
            .stDataFrame {
                overflow-x: auto;
            }
            .css-1n76uvr {
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("Exportación de Datos")
    
    # CSS para el botón de exportar
    st.markdown("""
        <style>
        .stDownloadButton button {
            background-color: #0066CC;
            color: white;
            font-weight: bold;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .stDownloadButton button:hover {
            background-color: #0052a3;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Agregar selector de fechas con mejor diseño
    st.markdown("##### Seleccione el rango de fechas para exportar")
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input(
            "Fecha de inicio",
            min_value=df['fecha_hora'].min().date(),
            max_value=df['fecha_hora'].max().date(),
            value=df['fecha_hora'].min().date()
        )
    with col2:
        fecha_fin = st.date_input(
            "Fecha de fin",
            min_value=df['fecha_hora'].min().date(),
            max_value=df['fecha_hora'].max().date(),
            value=df['fecha_hora'].max().date()
        )
    
    # Filtrar datos según las fechas seleccionadas
    df_filtered = df[
        (df['fecha_hora'].dt.date >= fecha_inicio) & 
        (df['fecha_hora'].dt.date <= fecha_fin)
    ]
    
    # Mostrar resumen del filtro con mejor diseño
    st.markdown(f"""
        <div style='padding: 1rem; background-color: rgba(28, 131, 225, 0.1); border-radius: 5px; margin: 1rem 0;'>
            <h6 style='margin: 0; color: #0066CC;'>Resumen de datos seleccionados:</h6>
            <p style='margin: 0.5rem 0 0 0;'>Período: {fecha_inicio} a {fecha_fin}</p>
            <p style='margin: 0.2rem 0 0 0;'>Total de registros: {len(df_filtered)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Agregar botón de exportación directa
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Exportar Datos Filtrados",
        data=csv,
        file_name=f'datos_osm27_{fecha_inicio}_{fecha_fin}.csv',
        mime='text/csv',
    )
    
    # Mostrar tabla de datos con Mito
    st.markdown("##### Vista previa de datos:")
    new_dfs, _ = spreadsheet(df_filtered)
    
    # Fin del programa
