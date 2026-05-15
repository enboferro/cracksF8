import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Estadísticas de Partido PRO", layout="wide")
st.title("📊 Registrador de Estadísticas Avanzado")

# 2. Inicializar el estado de la sesión
if "historial" not in st.session_state:
    # Creamos un DataFrame vacío para guardar cada evento del partido
    st.session_state.historial = pd.DataFrame(columns=["Hora", "Jugador", "Acción", "Resultado"])

if "inicio_partido" not in st.session_state:
    st.session_state.inicio_partido = None

# 3. Panel Lateral: Configuración del Partido
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Gestión de jugadores
    jugadores_input = st.text_area("Lista de jugadores (separados por coma):", 
                                   "Juan, Pedro, Carlos, Sofía, Luis")
    lista_jugadores = [j.strip() for j in jugadores_input.split(",") if j.strip()]
    
    st.markdown("---")
    
    # Control del tiempo del partido
    if st.session_state.inicio_partido is None:
        if st.button("▶️ Iniciar Partido / Cronómetro", type="primary", use_container_width=True):
            st.session_state.inicio_partido = datetime.now()
            st.rerun()
    else:
        tiempo_transcurrido = datetime.now() - st.session_state.inicio_partido
        minutos = int(tiempo_transcurrido.total_seconds() // 60)
        st.success(st.session_state.inicio_partido.strftime("Partido iniciado a las %H:%M"))
        
        if st.button("🔄 Reiniciar Todo", type="secondary", use_container_width=True):
            st.session_state.historial = pd.DataFrame(columns=["Hora", "Jugador", "Acción", "Resultado"])
            st.session_state.inicio_partido = None
            st.rerun()

# Función para registrar un evento
def registrar_evento(jugador, accion, resultado):
    if st.session_state.inicio_partido is None:
        st.error("❌ ¡Primero debes iniciar el partido en el panel lateral!")
        return

    # Calcular el minuto del partido
    tiempo_transcurrido = datetime.now() - st.session_state.inicio_partido
    minuto_partido = f"Min {int(tiempo_transcurrido.total_seconds() // 60)}'"
    
    # Añadir nueva fila al historial
    nueva_fila = pd.DataFrame([{
        "Hora": minuto_partido,
        "Jugador": jugador,
        "Acción": accion,
        "Resultado": resultado
    }])
    
    st.session_state.historial = pd.concat([st.session_state.historial, nueva_fila], ignore_index=True)

# --- CUERPO PRINCIPAL ---

if st.session_state.inicio_partido is None:
    st.warning("👈 Por favor, inicia el partido en el panel izquierdo para empezar a registrar.")
else:
    # 4. Selección de Jugador Activo
    st.subheader("🏃‍♂️ Selección de Jugador")
    jugador_activo = st.selectbox("¿Quién realiza la acción?", lista_jugadores)

    # 5. Botones de Registro
    st.subheader("⚽ Botonera de Eventos")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### **Pases**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Pase Bueno", key="pb", use_container_width=True):
                registrar_evento(jugador_activo, "Pase", "Bueno")
        with c2:
            if st.button("❌ Pase Malo", key="pm", use_container_width=True):
                registrar_evento(jugador_activo, "Pase", "Malo")

    with col2:
        st.markdown("### **Tiros**")
        c3, c4 = st.columns(2)
        with c3:
            if st.button("🎯 Tiro Bueno", key="tb", use_container_width=True):
                registrar_evento(jugador_activo, "Tiro", "Bueno")
        with c4:
            if st.button("🪵 Tiro Malo", key="tm", use_container_width=True):
                registrar_evento(jugador_activo, "Tiro", "Malo")

    st.markdown("---")

    # 6. Visualización de Estadísticas y Filtros
    st.subheader("📈 Panel de Estadísticas")
    
    # Filtro para ver estadísticas globales o por jugador específico
    opciones_filtro = ["Todos los Jugadores"] + lista_jugadores
    filtro_ver = st.selectbox("Ver estadísticas de:", opciones_filtro)
    
    # Filtrar el DataFrame según la selección
    df_filtrado = st.session_state.historial
    if filtro_ver != "Todos los Jugadores":
        df_filtrado = df_filtrado[df_filtrado["Jugador"] == filtro_ver]

    # Cálculos dinámicos
    pases_b = len(df_filtrado[(df_filtrado["Acción"] == "Pase") & (df_filtrado["Resultado"] == "Bueno")])
    pases_m = len(df_filtrado[(df_filtrado["Acción"] == "Pase") & (df_filtrado["Resultado"] == "Malo")])
    tiros_b = len(df_filtrado[(df_filtrado["Acción"] == "Tiro") & (df_filtrado["Resultado"] == "Bueno")])
    tiros_m = len(df_filtrado[(df_filtrado["Acción"] == "Tiro") & (df_filtrado["Resultado"] == "Malo")])
    
    tot_pases = pases_b + pases_m
    tot_tiros = tiros_b + tiros_m
    
    pct_pases = (pases_b / tot_pases * 100) if tot_pases > 0 else 0
    pct_tiros = (tiros_b / tot_tiros * 100) if tot_tiros > 0 else 0

    # Mostrar métricas del filtro seleccionado
    m1, m2 = st.columns(2)
    with m1:
        st.metric(label=f"Efectividad Pases ({filtro_ver})", value=f"{pct_pases:.1f}%", delta=f"{tot_pases} intentos")
        st.caption(f"Buenos: {pases_b} | Malos: {pases_m}")
    with m2:
        st.metric(label=f"Efectividad Tiros ({filtro_ver})", value=f"{pct_tiros:.1f}%", delta=f"{tot_tiros} intentos")
        st.caption(f"Buenos: {tiros_b} | Malos: {tiros_m}")

    st.markdown("---")

    # 7. Historial del Tiempo (Línea de sucesos)
    st.subheader("⏱️ Historial del Partido (Últimas acciones primero)")
    if not st.session_state.historial.empty:
        # Mostramos el historial ordenado a la inversa para ver lo más reciente arriba
        st.dataframe(st.session_state.historial.iloc[::-1], use_container_width=True)
    else:
        st.info("Aún no hay acciones registradas en este partido.")
