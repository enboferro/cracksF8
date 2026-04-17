import streamlit as st
import time

# Configuración para móvil (Pixel 10 Pro XL)
st.set_page_config(page_title="LUD F8 PRO", layout="wide")

# CSS para que parezca una App Nativa
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem; }
    .main-clock { font-size: 50px !important; font-weight: 800; text-align: center; color: #1d1d1d; margin: 0; }
    .stat-text { font-size: 12px; color: #666; text-align: center; }
    .player-card { 
        border: 1px solid #ddd; border-radius: 8px; padding: 5px; margin-bottom: 5px;
        background-color: #f9f9f9;
    }
    .stButton > button { width: 100%; height: 50px !important; border-radius: 8px; font-size: 14px !important; }
    /* Estilo para jugadores en pista */
    div.stButton > button[kind="primary"] { background-color: #28a745 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES ---
if 'players_stats' not in st.session_state:
    jugadores = ["Serra", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre", "Baeza", "Manu", "Toro", "Silla", "Jose", "Coque", "Nacho"]
    st.session_state.players_stats = {
        nom: {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False} 
        for nom in jugadores
    }
    st.session_state.update({
        'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None,
        'goles_lud': 0, 'goles_riv': 0
    })

s = st.session_state

# --- LÓGICA DEL CRONÓMETRO GENERAL ---
if s.running:
    ahora = time.time()
    diff = ahora - s.ultimo_click
    tiempo_actual = s.tiempo_acumulado + diff
    # Actualizar tiempos de jugadores en pista
    for p, stats in s.players_stats.items():
        if stats['in_pista']:
            stats['current_shift'] = ahora - stats['last_entry']
else:
    tiempo_actual = s.tiempo_acumulado

mins, secs = divmod(int(tiempo_actual), 60)

# --- CABECERA (MARCADOR Y CONTROL) ---
col1, col2, col3 = st.columns([1, 1.5, 1])
with col1:
    st.markdown(f"<h2 style='text-align:center;'>{s.goles_lud}</h2>", unsafe_allow_html=True)
    if st.button("⚽ LUD"): s.goles_lud += 1; st.rerun()

with col2:
    st.markdown(f"<div class='main-clock'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if not s.running:
        if c1.button("▶️"):
            s.running = True
            s.ultimo_click = time.time()
            for p in s.players_stats.values():
                if p['in_pista']: p['last_entry'] = s.ultimo_click
            st.rerun()
    else:
        if c1.button("⏸️"):
            s.running = False
            s.tiempo_acumulado += (time.time() - s.ultimo_click)
            for p in s.players_stats.values():
                if p['in_pista']:
                    p['total'] += p['current_shift']
                    p['current_shift'] = 0
            st.rerun()
    if c2.button("🔄"): st.session_state.clear(); st.rerun()

with col3:
    st.markdown(f"<h2 style='text-align:center;'>{s.goles_riv}</h2>", unsafe_allow_html=True)
    if st.button("⚽ RIV"): s.goles_riv += 1; st.rerun()

st.divider()

# --- LISTA DE JUGADORES (OPTIMIZADA MÓVIL) ---
st.markdown("### 🏃 Jugadores (Pista / Total)")

for nom, stats in s.players_stats.items():
    col_btn, col_info = st.columns([2, 1])
    
    with col_btn:
        # El botón cambia a color verde si está en pista
        btn_type = "primary" if stats['in_pista'] else "secondary"
        if st.button(f"{nom}", key=f"btn_{nom}", type=btn_type):
            if not stats['in_pista']:
                # ENTRAR A PISTA
                porteros = ["Serra", "Jose"]
                en_pista_campo = [p for p, stt in s.players_stats.items() if stt['in_pista'] and p not in porteros]
                
                if nom in porteros or len(en_pista_campo) < 7:
                    stats['in_pista'] = True
                    stats['last_entry'] = time.time() if s.running else None
            else:
                # SALIR A BANQUILLO
                stats['in_pista'] = False
                if s.running and stats['last_entry']:
                    stats['total'] += (time.time() - stats['last_entry'])
                stats['current_shift'] = 0
            st.rerun()

    with col_info:
        m_t, s_t = divmod(int(stats['total'] + (stats['current_shift'] if s.running else 0)), 60)
        m_c, s_c = divmod(int(stats['current_shift']), 60)
        st.markdown(f"**{m_t:02d}:{s_t:02d}**")
        st.markdown(f"<div class='stat-text'>Shift: {m_c:02d}:{s_c:02d}</div>", unsafe_allow_html=True)

# Auto-refresh
if s.running:
    time.sleep(1)
    st.rerun()
