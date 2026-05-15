import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# 1. Configuración de la página - Optimizada para Tablets
st.set_page_config(page_title="Stats Match iPad", layout="wide", initial_sidebar_state="collapsed")

# Estilo CSS para que los botones sean más grandes y fáciles de tocar en iPad
st.markdown("""
    <style>
    div.stButton > button {
        height: 3em;
        font-size: 20px !important;
        margin-bottom: 10px;
    }
    .main {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Estadísticas de Partido (iPad Edition)")

# 2. Inicializar estado
if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=["Hora", "Jugador", "Acción", "Resultado", "X", "Y"])
if "inicio_partido" not in st.session_state:
    st.session_state.inicio_partido = None

# 3. Sidebar (Panel de control)
with st.sidebar:
    st.header("⚙️ Configuración")
    jugadores_input = st.text_area("Jugadores:", "Juan, Pedro, Carlos, Sofía, Luis")
    lista_jugadores = [j.strip() for j in jugadores_input.split(",") if j.strip()]
    nombre_portero = st.text_input("Nombre del Portero:", "Portero 1")
    
    if st.session_state.inicio_partido is None:
        if st.button("▶️ Iniciar Partido", use_container_width=True):
            st.session_state.inicio_partido = datetime.now()
            st.rerun()
    else:
        if st.button("🔄 Reiniciar", use_container_width=True):
            st.session_state.historial = pd.DataFrame(columns=["Hora", "Jugador", "Acción", "Resultado", "X", "Y"])
            st.session_state.inicio_partido = None
            st.rerun()

def registrar_evento(jugador, accion, resultado, x=None, y=None):
    if st.session_state.inicio_partido:
        t = datetime.now() - st.session_state.inicio_partido
        minuto = f"{int(t.total_seconds() // 60)}'"
        nueva_fila = pd.DataFrame([{"Hora": minuto, "Jugador": jugador, "Acción": accion, "Resultado": resultado, "X": x, "Y": y}])
        st.session_state.historial = pd.concat([st.session_state.historial, nueva_fila], ignore_index=True)

# --- CUERPO PRINCIPAL ---
if st.session_state.inicio_partido is None:
    st.warning("👈 Inicia el partido en el menú lateral")
else:
    # Usamos Pestañas (Tabs) para separar Jugadores de Porteros (Ideal para iPad)
    tab1, tab2, tab3 = st.tabs(["🏃 JUGADORES", "🧤 PORTERO", "📊 RESUMEN"])

    with tab1:
        jugador_activo = st.selectbox("Jugador:", lista_jugadores)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Pases")
            if st.button("✅ Pase OK", key="p_ok", use_container_width=True):
                registrar_evento(jugador_activo, "Pase", "Bueno")
            if st.button("❌ Pase FALLO", key="p_ko", use_container_width=True):
                registrar_evento(jugador_activo, "Pase", "Malo")
        
        with col2:
            st.subheader("Tiros")
            if st.button("🎯 Tiro OK", key="t_ok", use_container_width=True):
                registrar_evento(jugador_activo, "Tiro", "Bueno")
            if st.button("🪵 Tiro FALLO", key="t_ko", use_container_width=True):
                registrar_evento(jugador_activo, "Tiro", "Malo")
        
        st.markdown("---")
        st.subheader("⚠️ Pérdidas 1vs1")
        px = st.slider("Posición Campo (Defensa 0 - 100 Ataque)", 0, 100, 50)
        if st.button("🚨 Registrar Pérdida aquí", type="primary", use_container_width=True):
            registrar_evento(jugador_activo, "Pérdida 1vs1", "Malo", x=px, y=50)

    with tab2:
        st.subheader(f"Portería: {nombre_portero}")
        c_port1, c_port2 = st.columns(2)
        
        with c_port1:
            if st.button("🧤 ¡PARADÓN!", type="primary", use_container_width=True):
                registrar_evento(nombre_portero, "Parada", "Bueno")
        with c_port2:
            if st.button("⚽ GOL RECIBIDO", use_container_width=True):
                registrar_evento(nombre_portero, "Parada", "Malo")
        
        # Estadísticas del portero
        df_p = st.session_state.historial[st.session_state.historial["Jugador"] == nombre_portero]
        paradas = len(df_p[df_p["Resultado"] == "Bueno"])
        goles = len(df_p[df_p["Resultado"] == "Malo"])
        total_tiros_recibidos = paradas + goles
        porcentaje_paradas = (paradas / total_tiros_recibidos * 100) if total_tiros_recibidos > 0 else 0
        
        st.metric("Efectividad del Portero", f"{porcentaje_paradas:.1f}%", f"{paradas} paradas de {total_tiros_recibidos} tiros")

    with tab3:
        # Mapa y Resumen (Adaptado para iPad)
        st.subheader("Mapa de Pérdidas")
        df_mapa = st.session_state.historial[st.session_state.historial["Acción"] == "Pérdida 1vs1"]
        
        fig = go.Figure()
        fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=60, fillcolor="ForestGreen", line=dict(color="white"))
        fig.add_trace(go.Scatter(x=df_mapa["X"], y=[30]*len(df_mapa), mode='markers', marker=dict(size=15, color='red', symbol='x')))
        fig.update_layout(width=700, height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Historial Rápido")
        st.dataframe(st.session_state.historial.iloc[::-1], use_container_width=True)
