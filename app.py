import streamlit as st
import time

# Configuración de pantalla para Tablet 8 pulgadas
st.set_page_config(page_title="LUD F8 Control", layout="wide")

st.markdown("""
    <style>
    /* Estilo para botones táctiles grandes */
    .stButton > button {
        width: 100%;
        height: 70px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 12px;
        border: 2px solid #4B2E2A;
    }
    .main-clock {
        font-size: 100px !important;
        font-family: 'monospace';
        font-weight: bold;
        text-align: center;
        color: #4B2E2A;
        padding: 0px;
        margin-top: -20px;
    }
    .score-box {
        font-size: 60px;
        font-weight: 900;
        text-align: center;
        line-height: 1;
    }
    .player-on {
        background-color: #00FF41 !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DEL ESTADO ---
if 'running' not in st.session_state:
    st.session_state.update({
        'running': False,
        'tiempo_acumulado': 0,
        'ultimo_click': None,
        'goles_lud': 0,
        'goles_riv': 0,
        'faltas_lud': 0,
        'faltas_riv': 0,
        'pista': []
    })

s = st.session_state

# --- LÓGICA DEL TIEMPO (ASCENDENTE) ---
if s.running:
    tiempo_actual = s.tiempo_acumulado + (time.time() - s.ultimo_click)
else:
    tiempo_actual = s.tiempo_acumulado

mins, secs = divmod(int(tiempo_actual), 60)
formato_tiempo = f"{mins:02d}:{secs:02d}"

# --- CABECERA: MARCADOR Y CRONO ---
col_lud, col_time, col_riv = st.columns([1, 2, 1])

with col_lud:
    st.markdown(f"<div class='score-box'>{s.goles_lud}</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>LEVANTE UD</p>", unsafe_allow_html=True)
    if st.button("⚽ + GOL"): s.goles_lud += 1; st.rerun()

with col_time:
    st.markdown(f"<div class='main-clock'>{formato_tiempo}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    if c1.button("▶️"):
        if not s.running:
            s.running = True
            s.ultimo_click = time.time()
            st.rerun()
    if c2.button("⏸️"):
        if s.running:
            s.tiempo_acumulado += (time.time() - s.ultimo_click)
            s.running = False
            st.rerun()
    if c3.button("🔄"):
        s.tiempo_acumulado = 0
        s.running = False
        st.rerun()

with col_riv:
    st.markdown(f"<div class='score-box'>{s.goles_riv}</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>RIVAL</p>", unsafe_allow_html=True)
    if st.button("⚽ + RIV"): s.goles_riv += 1; st.rerun()

st.divider()

# --- SECCIÓN DE FALTAS ---
f1, f2 = st.columns(2)
with f1:
    if st.button(f"FALTAS LUD: {s.faltas_lud}"): s.faltas_lud += 1; st.rerun()
with f2:
    if st.button(f"FALTAS RIVAL: {s.faltas_riv}"): s.faltas_riv += 1; st.rerun()

# --- GESTIÓN DE PLANTILLA F8 (7+1) ---
st.subheader(f"👥 Plantilla en Pista ({len([j for j in s.pista if j not in ['Serra', 'Jose']])} / 7 jugadores de campo)")

jugadores = ["Serra", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre", "Baeza", "Manu", "Toro", "Silla", "Jose", "Coque", "Nacho"]
cols = st.columns(3) # 3 columnas para que los botones sean muy anchos en 8"

for i, nombre in enumerate(jugadores):
    with cols[i % 3]:
        en_pista = nombre in s.pista
        # Marcamos visualmente si está en pista
        label = f"✅ {nombre}" if en_pista else f"🪑 {nombre}"
        
        if st.button(label, key=f"btn_{nombre}"):
            if en_pista:
                s.pista.remove(nombre)
            else:
                porteros = ["Serra", "Jose"]
                jugadores_campo = [j for j in s.pista if j not in porteros]
                
                # REGLA F8: Portero + 7 de campo
                if nombre in porteros or len(jugadores_campo) < 7:
                    s.pista.append(nombre)
                else:
                    st.warning("¡Ya hay 7 jugadores de campo!")
            st.rerun()

# Refresco para que el cronómetro se vea fluido
if s.running:
    time.sleep(1)
    st.rerun()
