import streamlit as st
import time

# Configuración de página
st.set_page_config(page_title="LUD F8 - Pixel Edition", layout="wide")

# CSS Avanzado para Responsive (Pixel 10 Pro XL y Tablets)
st.markdown("""
    <style>
    /* Contenedor principal */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Cronómetro adaptable */
    .main-clock {
        font-size: calc(40px + 4vw) !important;
        font-family: 'Courier New', Courier, monospace;
        font-weight: 800;
        text-align: center;
        color: #1d1d1d;
        line-height: 1;
        margin: 10px 0;
    }

    /* Marcador */
    .score-box {
        font-size: calc(30px + 3vw);
        font-weight: 900;
        text-align: center;
    }

    /* Botones de acción (Goles/Faltas) */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold !important;
        text-transform: uppercase;
    }

    /* Botones de Jugadores - Altura ajustable para no hacer scroll */
    div[data-testid="stVerticalBlock"] > div:has(button[key^="btn_"]) {
        margin-bottom: -10px;
    }
    
    .player-btn > div > button {
        height: 55px !important;
        font-size: 14px !important;
    }
    
    /* Quitar espacios innecesarios de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if 'running' not in st.session_state:
    st.session_state.update({
        'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None,
        'goles_lud': 0, 'goles_riv': 0, 'faltas_lud': 0, 'faltas_riv': 0, 'pista': []
    })

s = st.session_state

# Lógica de tiempo
if s.running:
    tiempo_actual = s.tiempo_acumulado + (time.time() - s.ultimo_click)
else:
    tiempo_actual = s.tiempo_acumulado

mins, secs = divmod(int(tiempo_actual), 60)

# --- INTERFAZ DINÁMICA ---

# Fila 1: Marcador y Tiempo
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown(f"<div class='score-box'>{s.goles_lud}</div>", unsafe_allow_html=True)
    if st.button("⚽ LUD"): 
        s.goles_lud += 1
        st.rerun()

with col2:
    st.markdown(f"<div class='main-clock'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
    c_start, c_stop, c_reset = st.columns(3)
    if c_start.button("▶️"):
        if not s.running:
            s.running = True
            s.ultimo_click = time.time()
            st.rerun()
    if c_stop.button("⏸️"):
        if s.running:
            s.tiempo_acumulado += (time.time() - s.ultimo_click)
            s.running = False
            st.rerun()
    if c_reset.button("🔄"):
        s.tiempo_acumulado = 0
        s.running = False
        st.rerun()

with col3:
    st.markdown(f"<div class='score-box'>{s.goles_riv}</div>", unsafe_allow_html=True)
    if st.button("⚽ RIV"): 
        s.goles_riv += 1
        st.rerun()

# Fila 2: Faltas
st.write("")
f_l, f_r = st.columns(2)
if f_l.button(f"Faltas LUD: {s.faltas_lud}"): 
    s.faltas_lud += 1
    st.rerun()
if f_r.button(f"Faltas RIVAL: {s.faltas_riv}"): 
    s.faltas_riv += 1
    st.rerun()

st.markdown("---")

# Fila 3: Jugadores (Grid adaptable)
# En móviles modernos, 2 o 3 columnas es lo ideal para no fallar el dedo
st.markdown(f"**Pista (F8): {len([j for j in s.pista if j not in ['Serra', 'Jose']])}/7**")
jugadores = ["Serra", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre", "Baeza", "Manu", "Toro", "Silla", "Jose", "Coque", "Nacho"]

# Usamos 3 columnas para el Pixel 10 Pro XL (pantalla ancha)
cols = st.columns(3)

for i, nombre in enumerate(jugadores):
    with cols[i % 3]:
        en_pista = nombre in s.pista
        tipo = "✅" if en_pista else "⬜"
        # Usamos contenedores para aplicar estilo específico a estos botones
        if st.button(f"{tipo} {nombre}", key=f"btn_{nombre}"):
            if en_pista:
                s.pista.remove(nombre)
            else:
                porteros = ["Serra", "Jose"]
                if nombre in porteros or len([j for j in s.pista if j not in porteros]) < 7:
                    s.pista.append(nombre)
            st.rerun()

# Auto-refresh
if s.running:
    time.sleep(0.5)
    st.rerun()
