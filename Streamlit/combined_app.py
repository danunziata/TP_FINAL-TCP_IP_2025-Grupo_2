import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mitosheet.streamlit.v1 import spreadsheet
from mitosheet.streamlit.v1.spreadsheet import _get_mito_backend
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title='Sistema de Monitoreo OSM27', layout='wide', page_icon=':electric_plug:')

# Header
t1, t2 = st.columns((0.07,1)) 
t1.image('unrc_logo.jpg', width = 120)
t2.title("Sistema de Monitoreo OSM27 - IPSEP UNRC")
t2.markdown("**UNRC - Facultad de Ingeniería**")

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
    
    # Métricas
    m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))
    
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
     
    # Gráficos superiores en 3 columnas
    g1, g2, g3 = st.columns((1,1,1))
    
    # Primer gráfico - Eventos de reconexión
    fig = px.scatter(df, x='fecha_hora', y='estado', template='seaborn')
    fig.update_traces(marker=dict(size=10, color='#264653'))
    fig.update_layout(title_text="Eventos de reconexión en el tiempo",
                     title_x=0,
                     margin=dict(l=0,r=10,b=10,t=30), 
                     yaxis_title="Estado",
                     xaxis_title="Tiempo")
    g1.plotly_chart(fig, use_container_width=True) 
    
    # Segundo gráfico - Variable seleccionada
    fig = go.Figure()
    for var in variable_options[selected_var]:
        fig.add_trace(go.Scatter(x=df['fecha_hora'], 
                               y=df[var], 
                               name=var.upper(), 
                               line=dict(width=2)))
    
    fig.update_layout(title_text=f"{selected_var} en tiempo real",
                     title_x=0,
                     margin=dict(l=0,r=10,b=10,t=30), 
                     yaxis_title=f"{selected_var} ({unidad})",
                     xaxis_title="Tiempo",
                     legend=dict(orientation="h",yanchor="bottom",y=0.9,xanchor="right",x=0.99))
    g2.plotly_chart(fig, use_container_width=True)  
    
    # Tercer gráfico - Factor de potencia o análisis adicional
    if selected_var == 'Potencias':
        fig = px.line(df, x='fecha_hora', y='fp', template='seaborn')
        titulo = "Factor de Potencia"
        y_titulo = "Factor de Potencia"
    else:
        # Calcular valores RMS para la variable seleccionada
        df_rms = df[variable_options[selected_var]].rolling(window=20).mean()
        fig = px.line(df_rms, template='seaborn')
        titulo = f"Valores RMS - {selected_var}"
        y_titulo = f"Valor RMS ({unidad})"
    
    fig.update_layout(title_text=titulo,
                     title_x=0,
                     margin=dict(l=0,r=10,b=10,t=30), 
                     yaxis_title=y_titulo,
                     xaxis_title="Tiempo")
    g3.plotly_chart(fig, use_container_width=True) 

    # Sección de Mito (hoja de cálculo interactiva)
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
