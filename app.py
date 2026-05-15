import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración de la página
st.set_page_config(page_title="Estadísticas de Partido PRO+", layout="wide")
st.title("📊 Registrador Estadístico con Mapa de Calor")

# 2. Inicializar el estado de la sesión
if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=["Hora", "Jugador", "Acción", "Resultado", "X", "Y"])

if "inicio_partido" not in st.session_state:
    st.session_state.inicio_partido = None

# 3. Panel Lateral: Configuración del Partido
with st.sidebar:
    st.header("⚙️ Configuración")
    jugadores_input = st.text_area("Lista de jugadores:", "Juan, Pedro, Carlos, Sofía, Luis")
    lista_jugadores = [j.strip() for j in jugadores_input.split(",") if j.strip()]
    
    st.markdown("---")
    
    if st.session_state.inicio_partido is None:
        if st.button("▶️ Iniciar Partido", type="primary", use_container_width=True):
            st.session_state.inicio_partido = datetime.now()
            st.rerun()
    else:
        st.success(st.session_state.inicio_partido.strftime("Partido iniciado a las %H:%M"))
        if st.button("🔄 Reiniciar Todo", type="secondary", use_container_width=True):
            st.session_state.historial = pd.DataFrame(columns=["Hora", "Jugador", "Acción", "Resultado", "X", "Y"])
            st.session_state.inicio_partido = None
            st.rerun()

# Función para registrar un evento
def registrar_evento(jugador, accion, resultado, x=None, y=None):
    if st.session_state.inicio_partido is None:
        st.error("❌ ¡Primero debes iniciar el partido!")
        return

    tiempo_transcurrido = datetime.now() - st.session_state.inicio_partido
    minuto_partido = f"Min {int(tiempo_transcurrido.total_seconds() // 60)}'"
    
    nueva_fila = pd.DataFrame([{
        "Hora": minuto_partido,
        "Jugador": jugador,
        "Acción": accion,
        "Resultado": resultado,
        "X": x,
        "Y": y
    }])
    
    st.session_state.historial = pd.concat([st.session_state.historial, nueva_fila], ignore_index=True)

# --- CUERPO PRINCIPAL ---

if st.session_state.inicio_partido is None:
    st.warning("👈 Por favor, inicia el partido en el panel izquierdo para empezar.")
else:
    # Selector de Jugador
    st.subheader("🏃‍♂️ Selección de Jugador")
    jugador_activo = st.selectbox("¿Quién realiza la acción?", lista_jugadores)

    # Botonera de Eventos
    st.subheader("⚽ Botonera de Eventos")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### **Pases**")
        if st.button("✅ Pase Bueno", key="pb", use_container_width=True):
            registrar_evento(jugador_activo, "Pase", "Bueno")
        if st.button("❌ Pase Malo", key="pm", use_container_width=True):
            registrar_evento(jugador_activo, "Pase", "Malo")

    with col2:
        st.markdown("### **Tiros**")
        if st.button("🎯 Tiro Bueno", key="tb", use_container_width=True):
            registrar_evento(jugador_activo, "Tiro", "Bueno")
        if st.button("🪵 Tiro Malo", key="tm", use_container_width=True):
            registrar_evento(jugador_activo, "Tiro", "Malo")

    with col3:
        st.markdown("### **Duelos / Pérdidas**")
        # Aquí añadimos el selector de coordenadas para las pérdidas
        st.write("Selecciona dónde se perdió el balón en el mapa de abajo antes de pulsar:")
        posX = st.slider("Posición X (0=Tu Portería, 100=Rival)", 0, 100, 50)
        posY = st.slider("Posición Y (0=Izquierda, 100=Derecha)", 0, 100, 50)
        
        if st.button("⚠️ Pérdida en 1vs1", key="perdidav1", type="primary", use_container_width=True):
            registrar_evento(jugador_activo, "Pérdida 1vs1", "Malo", x=posX, y=posY)

    st.markdown("---")

    # PANEL DE RENDIMIENTO Y ANÁLISIS
    st.subheader("📈 Panel de Análisis")
    
    opciones_filtro = ["Todos los Jugadores"] + lista_jugadores
    filtro_ver = st.selectbox("Filtrar análisis por:", opciones_filtro)
    
    df_filtrado = st.session_state.historial
    if filtro_ver != "Todos los Jugadores":
        df_filtrado = df_filtrado[df_filtrado["Jugador"] == filtro_ver]

    # Renderizar métricas básicas
    pases_b = len(df_filtrado[(df_filtrado["Acción"] == "Pase") & (df_filtrado["Resultado"] == "Bueno")])
    pases_m = len(df_filtrado[(df_filtrado["Acción"] == "Pase") & (df_filtrado["Resultado"] == "Malo")])
    tot_pases = pases_b + pases_m
    pct_pases = (pases_b / tot_pases * 100) if tot_pases > 0 else 0

    # Contar pérdidas específicas
    total_perdidas = len(df_filtrado[df_filtrado["Acción"] == "Pérdida 1vs1"])

    m1, m2 = st.columns(2)
    with m1:
        st.metric(label=f"Efectividad Pases ({filtro_ver})", value=f"{pct_pases:.1f}%")
    with m2:
        st.metric(label=f"Pérdidas en 1vs1 ({filtro_ver})", value=f"{total_perdidas} balones", delta="Evitar en zona crítica", delta_color="inverse")

    st.markdown("---")

    # MAPA DEL CAMPO Y RANKING
    col_mapa, col_ranking = st.columns([2, 1])

    with col_mapa:
        st.subheader("🗺️ Mapa de Pérdidas de Balón")
        
        # Filtrar solo las filas que tienen coordenadas (pérdidas)
        df_mapa = df_filtrado[df_filtrado["X"].notna()]
        
        # Crear un campo de fútbol visual con Plotly
        fig = go.Figure()
        
        # Dibujar líneas del campo (Fondo verde)
        fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, fillcolor="rgba(34, 139, 34, 0.6)", line=dict(color="white", width=2))
        fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(color="white", width=2)) # Línea de medio campo
        fig.add_shape(type="circle", x0=40, y0=40, x1=60, y1=60, line=dict(color="white", width=2)) # Círculo central
        
        # Añadir los puntos de pérdidas de balón si existen
        if not df_mapa.empty:
            fig.add_trace(go.Scatter(
                x=df_mapa["X"], y=df_mapa["Y"],
                mode='markers+text',
                marker=dict(size=12, color='red', symbol='x'),
                text=df_mapa["Jugador"] + " (" + df_mapa["Hora"] + ")",
                textposition="top center",
                name="Pérdida"
            ))
        
        fig.update_layout(
            xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, visible=False),
            yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, visible=False),
            width=600, height=400, margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_ranking:
        st.subheader("🏆 ¿Quién pierde más balones?")
        df_perdidas_global = st.session_state.historial[st.session_state.historial["Acción"] == "Pérdida 1vs1"]
        
        if not df_perdidas_global.empty:
            # Contamos cuántas pérdidas tiene cada jugador y creamos un ranking
            ranking_perdidas = df_perdidas_global["Jugador"].value_counts().reset_index()
            ranking_perdidas.columns = ["Jugador", "Pérdidas Totales"]
            st.dataframe(ranking_perdidas, use_container_width=True, hide_index=True)
        else:
            st.info("Ningún jugador ha perdido balones en 1vs1 todavía.")

    st.markdown("---")
    st.subheader("⏱️ Historial Completo")
    st.dataframe(st.session_state.historial.iloc[::-1], use_container_width=True)
