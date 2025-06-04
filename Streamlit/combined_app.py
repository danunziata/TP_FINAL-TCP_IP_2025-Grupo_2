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
    
    # Contenedor para los gráficos
    with st.container():
        # Primer gráfico - Eventos de reconexión
        with st.container():
            fig = px.scatter(df, x='fecha_hora', y='estado', template='seaborn')
        fig.update_traces(marker=dict(size=10, color='#264653'))
        fig.update_layout(
            title=dict(
                text="Eventos de reconexión en el tiempo",
                x=0,
                font=dict(size=20)
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="Estado",
            xaxis_title="Tiempo",
            height=400,  # Altura fija para mejor visualización
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")  # Separador visual
        
        # Segundo gráfico - Variable seleccionada
        fig = go.Figure()
        colors = ['#264653', '#2a9d8f', '#e9c46a']  # Color scheme
        
        for i, var in enumerate(variable_options[selected_var]):
            fig.add_trace(go.Scatter(
                x=df['fecha_hora'], 
                y=df[var], 
                name=var.upper(), 
                line=dict(width=2, color=colors[i])
            ))
        
        # Configuración específica según el tipo de variable
        if selected_var == 'Tensiones':
            y_range = [0, max(df[['va', 'vb', 'vc']].max()) * 1.1]
            fig.add_hline(y=220, line_dash="dash", line_color="red", annotation_text="Tensión nominal")
        elif selected_var == 'Corrientes':
            y_range = [0, max(df[['ia', 'ib', 'ic']].max()) * 1.1]
        else:  # Potencias
            y_range = [min(df[['p_act', 'p_react']].min()) * 1.1, 
                      max(df[['p_act', 'p_react']].max()) * 1.1]
        
        fig.update_layout(
            title=dict(
                text=f"{selected_var} en tiempo real",
                x=0,
                font=dict(size=20)
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(245,245,245,1)',
            yaxis=dict(
                title=f"{selected_var} ({unidad})",
                range=y_range,
                gridcolor='white'
            ),
            xaxis=dict(
                title="Tiempo",
                gridcolor='white'
            ),
            height=450,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.8)'
            ),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")  # Separador visual
        
        # Tercer gráfico - Análisis específico según variable
        if selected_var == 'Potencias':
            # Gráfico de factor de potencia y potencias
            fig = make_subplots(rows=2, cols=1, 
                              subplot_titles=("Factor de Potencia", "Potencia Activa vs Reactiva"),
                              vertical_spacing=0.15)
            
            fig.add_trace(
                go.Scatter(x=df['fecha_hora'], y=df['fp'], name="Factor de Potencia", 
                          line=dict(color='#264653')),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df['fecha_hora'], y=df['p_act'], name="P. Activa",
                          line=dict(color='#2a9d8f')),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['fecha_hora'], y=df['p_react'], name="P. Reactiva",
                          line=dict(color='#e9c46a')),
                row=2, col=1
            )
            
        else:
            # Valores RMS y análisis de desbalance
            df_rms = df[variable_options[selected_var]].rolling(window=20).mean()
            max_vals = df_rms.max()
            min_vals = df_rms.min()
            desbalance = ((max_vals - min_vals) / max_vals * 100).mean()
            
            fig = make_subplots(rows=1, cols=1,
                              subplot_titles=(f"Valores RMS y Desbalance: {desbalance:.1f}%"))
            
            for i, var in enumerate(variable_options[selected_var]):
                fig.add_trace(
                    go.Scatter(x=df['fecha_hora'], y=df_rms[var], 
                              name=f"{var.upper()} RMS", line=dict(color=colors[i]))
                )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(245,245,245,1)',
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
    
    st.header("Editor de Datos Interactivo")
    
    # Mostrar hoja de cálculo Mito con los datos actuales
    new_dfs, code = spreadsheet(df)
    
    if code:
        st.subheader("Código Python Generado")
        st.code(code)
    
    # Función para limpiar caché
    def clear_mito_backend_cache():
        _get_mito_backend.clear()

    @st.cache_resource
    def get_cached_time():
        return {"last_executed_time": None}

    def try_clear_cache():
        CLEAR_DELTA = timedelta(hours=12)
        current_time = datetime.now()
        cached_time = get_cached_time()
        if cached_time["last_executed_time"] is None or cached_time["last_executed_time"] + CLEAR_DELTA < current_time:
            clear_mito_backend_cache()
            cached_time["last_executed_time"] = current_time

    try_clear_cache()
