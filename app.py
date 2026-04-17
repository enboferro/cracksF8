import streamlit as st
import time

# Configuración para aprovechar cada píxel del Pixel 10 Pro XL
st.set_page_config(page_title="LUD F8 PRO - Compact", layout="wide")

st.markdown("""
    <style>
    /* Eliminar márgenes de Streamlit para ganar pantalla */
    .block-container { padding: 0.5rem; }
    
    /* Cronómetro y Marcador ultra-compacto */
    .main-clock { font-size: 45px !important; font-weight: 800; text-align: center; line-height: 1; margin: 0; }
    .score-val { font-size: 40px; font-weight: 900; text-align: center; }
    
    /* Grid de jugadores */
    .player-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 2px;
        background-color: #f1f1f1;
    }
    
    /* Botones de jugador ajustados para 3 columnas */
    div.stButton > button {
        width: 100%;
        height: 65px !important;
        padding: 0px !important;
        border-radius: 8px;
        line-height: 1.2;
    }
    
    /* Texto de tiempos dentro del botón o muy cerca */
    .time-overlay {
        font-size: 10px !important;
        font-family: monospace;
        line-height: 1;
        margin-top: -15px;
        pointer-events: none;
    }
    
    /* Quitar padding entre columnas */
    [data-testid="column"] { padding: 0 2px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if 'players_stats' not in st.session_state:
    jugadores = ["Serra", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre", "Baeza", "Manu", "Toro", "Silla", "Jose", "Coque", "Nacho"]
    st.session_state.players_stats = {
        nom: {'total': 0, 'current_shift': 0, 'last_entry': None, 'in_pista': False} 
        for nom in jugadores
    }
    st.session_state.update({'running': False, 'tiempo_acumulado': 0, 'ultimo_click': None, 'goles_lud': 0, 'goles_riv': 0})

s = st.session_state

# --- LÓGICA CRONO ---
if s.running:
    ahora = time.time()
    tiempo_actual = s.tiempo_acumulado + (ahora - s.ultimo_click)
    for p, stats in s.players_stats.items():
        if stats['in_pista']:
            stats['current_shift'] = ahora - stats['last_entry']
else:
    tiempo_actual = s.tiempo_acumulado

mins, secs = divmod(int(tiempo_actual), 60)

# --- CABECERA (3 COLUMNAS) ---
c_lud, c_mid, c_riv = st.columns([1, 1.5, 1])
with c_lud:
    st.markdown(f"<div class='score-val'>{s.goles_lud}</div>", unsafe_allow_html=True)
    if st.button("⚽ LUD"): s.goles_lud += 1; st.rerun()

with c_mid:
    st.markdown(f"<div class='main-clock'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    if b1.button("▶️" if not s.running else "⏸️"):
        if not s.running:
            s.running = True; s.ultimo_click = time.time()
            for p in s.players_stats.values():
                if p['in_pista']: p['last_entry'] = s.ultimo_click
        else:
            s.running = False; s.tiempo_acumulado += (time.time() - s.ultimo_click)
            for p in s.players_stats.values():
                if p['in_pista']: p['total'] += p['current_shift']; p['current_shift'] = 0
        st.rerun()
    if b2.button("🔄"): st.session_state.clear(); st.rerun()
    # Botón para descargar el resumen si es necesario
    if b3.button("📥"): st.toast("Datos guardados")

with c_riv:
    st.markdown(f"<div class='score-val'>{s.goles_riv}</div>", unsafe_allow_html=True)
    if st.button("⚽ RIV"): s.goles_riv += 1; st.rerun()

st.write("") # Espaciador mínimo

# --- GRID DE JUGADORES (3 COLUMNAS) ---
# Calculamos cuántos hay de campo
p_campo = [p for p, stt in s.players_stats.items() if stt['in_pista'] and p not in ["Serra", "Jose"]]
st.markdown(f"<p style='text-align:center; margin:0;'><b>Pista: {len(p_campo)}/7</b></p>", unsafe_allow_html=True)

cols = st.columns(3)
for i, (nom, stats) in enumerate(s.players_stats.items()):
    with cols[i % 3]:
        # Formateo de tiempos
        t_total = stats['total'] + (stats['current_shift'] if s.running and stats['in_pista'] else 0)
        m_t, s_t = divmod(int(t_total), 60)
        m_c, s_c = divmod(int(stats['current_shift']), 60)
        
        # El nombre y los tiempos van en el mismo bloque visual
        btn_label = f"{nom}\n{m_t:02d}:{s_t:02d} | {m_c:02d}:{s_c:02d}"
        
        if st.button(btn_label, key=f"btn_{nom}", type="primary" if stats['in_pista'] else "secondary"):
            if not stats['in_pista']:
                if nom in ["Serra", "Jose"] or len(p_campo) < 7:
                    stats['in_pista'] = True
                    stats['last_entry'] = time.time() if s.running else None
            else:
                stats['in_pista'] = False
                if s.running and stats['last_entry']:
                    stats['total'] += (time.time() - stats['last_entry'])
                stats['current_shift'] = 0
            st.rerun()

if s.running:
    time.sleep(1)
    st.rerun()
