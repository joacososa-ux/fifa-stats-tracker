import streamlit as st
import pandas as pd

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA WEB Y ESTILOS VISUALES (MÁS GRANDE)
# ============================================================================
st.set_page_config(
    page_title="FIFA Stats Tracker",
    page_icon="⚽",
    layout="centered"
)

# Inyectamos CSS personalizado para hacer la interfaz ligeramente más grande,
# con botones más llamativos y tipografías más legibles.
st.markdown("""
    <style>
        /* Aumentar el tamaño de fuente base de la app */
        html, body, [class*="css"] {
            font-size: 1.1rem !important;
        }
        /* Hacer los títulos principales más imponentes */
        h1 {
            font-size: 3rem !important;
            font-weight: 800 !important;
        }
        h2 {
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        h3 {
            font-size: 1.5rem !important;
        }
        /* Hacer las pestañas (Tabs) más grandes y legibles */
        .stTabs [data-baseweb="tab"] {
            font-size: 1.25rem !important;
            font-weight: bold !important;
            padding: 10px 20px !important;
        }
        /* Estilizar botones para que sean más grandes y cómodos */
        div.stButton > button {
            font-size: 1.1rem !important;
            padding: 0.5rem 1rem !important;
            border-radius: 8px !important;
        }
        /* Tarjetas de destacados con sombra y bordes redondeados */
        .metric-card {
            background-color: rgba(250, 250, 250, 0.1);
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# MEMORIA CACHÉ (Session State)
# ============================================================================
if "jugadores" not in st.session_state:
    st.session_state.jugadores = []

if "torneos" not in st.session_state:
    st.session_state.torneos = []

# Mensajes temporales que sobreviven a la recarga de página st.rerun()
if "mensaje_exito_jugador" not in st.session_state:
    st.session_state.mensaje_exito_jugador = None

if "mensaje_exito_torneo" not in st.session_state:
    st.session_state.mensaje_exito_torneo = None

if "mensaje_error_jugador" not in st.session_state:
    st.session_state.mensaje_error_jugador = None

if "lanzar_globos" not in st.session_state:
    st.session_state.lanzar_globos = False

# --- Funciones auxiliares ---
def buscar_jugador_por_id(id_j):
    for j in st.session_state.jugadores:
        if j["id"] == id_j:
            return j
    return None

# ============================================================================
# EFECTO VISUAL: Globos de Campeón 🎈
# ============================================================================
if st.session_state.lanzar_globos:
    st.balloons()
    st.session_state.lanzar_globos = False

# ============================================================================
# TÍTULO PRINCIPAL DE LA PÁGINA (Tamaño XL)
# ============================================================================
st.markdown("<h1 style='text-align: center;'>⚽ FIFA Stats Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.25rem; color: gray;'>¡Llevá el control absoluto de las vitrinas de tu grupo de amigos!</p>", unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# NAVEGACIÓN POR PESTAÑAS (Tabs actualizadas)
# ============================================================================
tab_ranking, tab_torneo, tab_amigos, tab_historial = st.tabs([
    "🏆 Salón de la Fama", 
    "🔥 Registrar Torneo", 
    "👥 Amigos", # Nombre modificado de "Añadir Amigo" a "Amigos"
    "📜 Historial"
])

# ----------------------------------------------------------------------------
# PESTAÑA 1: SALÓN DE LA FAMA (RANKING + DESTACADOS ESPECIALES + AJUSTES)
# ----------------------------------------------------------------------------
with tab_ranking:
    if not st.session_state.jugadores:
        st.info("👋 ¡Bienvenido! Registra a tus amigos en la pestaña 👥 Amigos para empezar a sumar estadísticas.")
    else:
        # 1. SECCIÓN DE DESTACADOS ESPECIALES (Métricas destacadas)
        st.markdown("### 🔥 Destacados de la Temporada")
        col_rey, col_sotano = st.columns(2)
        
        # Cálculo del Rey de Copas (Ligas + Copas)
        rey_nombre = "Nadie aún"
        rey_titulos = 0
        for j in st.session_state.jugadores:
            tot = j["ligas"] + j["copas"]
            if tot > rey_titulos:
                rey_titulos = tot
                rey_nombre = j["nombre"]
            elif tot == rey_titulos and rey_titulos > 0:
                # Caso de empate, sumamos el nombre
                if j["nombre"] not in rey_nombre:
                    rey_nombre += f", {j['nombre']}"
        
        # Cálculo de la Víctima del Descenso (Mayor cantidad de descensos)
        victima_nombre = "Nadie aún"
        max_descensos = 0
        for j in st.session_state.jugadores:
            desc = j["descensos"]
            if desc > max_descensos:
                max_descensos = desc
                victima_nombre = j["nombre"]
            elif desc == max_descensos and max_descensos > 0:
                if j["nombre"] not in victima_nombre:
                    victima_nombre += f", {j['nombre']}"

        with col_rey:
            st.markdown(f"""
                <div class="metric-card" style="border-top: 5px solid #FFD700;">
                    <span style="font-size: 2.2rem;">👑</span>
                    <h4 style="margin: 5px 0; color: #FFD700; font-size: 1.2rem;">REY DE COPAS</h4>
                    <p style="font-size: 1.6rem; font-weight: bold; margin: 0;">{rey_nombre}</p>
                    <small style="color: gray;">{rey_titulos} título(s) total(es)</small>
                </div>
            """, unsafe_allow_html=True)
            
        with col_sotano:
            st.markdown(f"""
                <div class="metric-card" style="border-top: 5px solid #FF4B4B;">
                    <span style="font-size: 2.2rem;">💀</span>
                    <h4 style="margin: 5px 0; color: #FF4B4B; font-size: 1.2rem;">SÓTANO DE LA TABLA</h4>
                    <p style="font-size: 1.6rem; font-weight: bold; margin: 0;">{victima_nombre}</p>
                    <small style="color: gray;">{max_descensos} descenso(s)</small>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # 2. TABLA GENERAL
        st.markdown("### 🏆 Tabla General de Posiciones")
        df = pd.DataFrame(st.session_state.jugadores)
        df["Total ⭐"] = df["ligas"] + df["copas"]
        df = df.rename(columns={
            "nombre": "Crack",
            "ligas": "Ligas 🏆",
            "copas": "Copas 🥇",
            "descensos": "Descensos 💀"
        })
        df = df.sort_values(by=["Total ⭐", "Ligas 🏆", "Descensos 💀"], ascending=[False, False, True])
        df.index = range(1, len(df) + 1)
        
        st.dataframe(df[["Crack", "Total ⭐", "Ligas 🏆", "Copas 🥇", "Descensos 💀"]], use_container_width=True)

        # 3. CONTROL DE AJUSTES MANUALES (Para sumar/restar rápido con botones)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚙️ Ajuste de Puntos Manual (Suma / Resta Rápida)"):
            st.markdown("Utilizá esta sección para configurar las estadísticas iniciales de tus amigos sin tener que crear torneos desde cero.")
            
            # Selector de jugador
            lista_nombres_ajuste = [j["nombre"] for j in st.session_state.jugadores]
            col_jug, col_stat, col_btn = st.columns([2, 2, 1.5])
            
            with col_jug:
                jugador_a_ajustar = st.selectbox("Selecciona un amigo:", lista_nombres_ajuste, key="sb_ajuste_jugador")
            with col_stat:
                stat_a_ajustar = st.selectbox("Estadística a modificar:", ["Ligas", "Copas", "Descensos"], key="sb_ajuste_stat")
            with col_btn:
                st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True) # Espaciador para alinear botones
                sub_col1, sub_col2 = st.columns(2)
                
                # Buscamos la referencia del jugador seleccionado
                referencia_jugador = next(j for j in st.session_state.jugadores if j["nombre"] == jugador_a_ajustar)
                
                with sub_col1:
                    if st.button("➖", key="btn_restar_stat", help="Restar 1 punto"):
                        clave = "ligas" if stat_a_ajustar == "Ligas" else ("copas" if stat_a_ajustar == "Copas" else "descensos")
                        referencia_jugador[clave] = max(0, referencia_jugador[clave] - 1)
                        st.rerun()
                with sub_col2:
                    if st.button("➕", key="btn_sumar_stat", help="Sumar 1 punto"):
                        clave = "ligas" if stat_a_ajustar == "Ligas" else ("copas" if stat_a_ajustar == "Copas" else "descensos")
                        referencia_jugador[clave] += 1
                        st.rerun()

# ----------------------------------------------------------------------------
# PESTAÑA 2: REGISTRAR TORNEO
# ----------------------------------------------------------------------------
with tab_torneo:
    st.header("🎮 Registrar Nueva Competencia")
    
    if st.session_state.mensaje_exito_torneo:
        st.success(st.session_state.mensaje_exito_torneo)
        st.session_state.mensaje_exito_torneo = None
    
    if len(st.session_state.jugadores) < 2:
        st.warning("⚠️ Necesitás registrar al menos 2 amigos en la plantilla para poder armar un torneo.")
    else:
        nombre_torneo = st.text_input("Nombre del torneo", placeholder="Ej: Champions de Living 2026")
        tipo_torneo = st.selectbox("Formato del torneo", ["Liga", "Copa"])
        
        lista_nombres = [j["nombre"] for j in st.session_state.jugadores]
        participantes_nombres = st.multiselect("¿Quiénes jugaron?", lista_nombres)
        
        if participantes_nombres:
            st.markdown("---")
            campeon_nombre = st.selectbox("👑 ¿Quién salió Campeón?", participantes_nombres)
            
            hubo_descenso = st.checkbox("¿Hubo descenso / último puesto?")
            descendido_nombre = None
            
            if hubo_descenso:
                posibles_descendidos = [n for n in participantes_nombres if n != campeon_nombre]
                if posibles_descendidos:
                    descendido_nombre = st.selectbox("💀 ¿Quién quedó último?", posibles_descendidos)
                else:
                    st.caption("Debe haber más participantes para asignar un descenso.")

            if st.button("Guardar Torneo 💾", type="primary"):
                if not nombre_torneo.strip():
                    st.error("Por favor, ingresá un nombre para el torneo.")
                else:
                    for j in st.session_state.jugadores:
                        if j["nombre"] == campeon_nombre:
                            if tipo_torneo == "Liga":
                                j["ligas"] += 1
                            else:
                                j["copas"] += 1
                        
                        if hubo_descenso and j["nombre"] == descendido_nombre:
                            j["descensos"] += 1
                    
                    nuevo_torneo = {
                        "nombre": nombre_torneo,
                        "tipo": tipo_torneo,
                        "campeon": campeon_nombre,
                        "descenso": descendido_nombre if hubo_descenso else "Ninguno"
                    }
                    st.session_state.torneos.append(nuevo_torneo)
                    
                    st.session_state.mensaje_exito_torneo = f"¡Torneo '{nombre_torneo}' registrado! Las vitrinas fueron actualizadas."
                    st.session_state.lanzar_globos = True
                    st.rerun()

# ----------------------------------------------------------------------------
# PESTAÑA 3: GESTIÓN DE AMIGOS (AGREGAR Y ELIMINAR EN UN SOLO LUGAR)
# ----------------------------------------------------------------------------
with tab_amigos:
    st.header("👥 Gestión de Plantilla de Amigos")
    
    # Mostramos alertas si existen de acciones previas
    if st.session_state.mensaje_exito_jugador:
        st.success(st.session_state.mensaje_exito_jugador)
        st.session_state.mensaje_exito_jugador = None
        
    if st.session_state.mensaje_error_jugador:
        st.error(st.session_state.mensaje_error_jugador)
        st.session_state.mensaje_error_jugador = None

    col_agregar, col_eliminar = st.columns(2)
    
    # SECCIÓN DE AGREGAR AMIGO
    with col_agregar:
        st.markdown("### 👤 Añadir Amigo")
        nuevo_nombre = st.text_input("Nombre del nuevo integrante:", placeholder="Ej: Marcos", key="input_nuevo_nombre")
        
        if st.button("Fichar Jugador 📝", use_container_width=True):
            if not nuevo_nombre.strip():
                st.session_state.mensaje_error_jugador = "El nombre no puede estar vacío."
                st.rerun()
            elif nuevo_nombre.strip() in [j["nombre"] for j in st.session_state.jugadores]:
                st.session_state.mensaje_error_jugador = f"¡El jugador {nuevo_nombre.strip()} ya está en la lista!"
                st.rerun()
            else:
                nuevo_id = max([j["id"] for j in st.session_state.jugadores], default=0) + 1
                st.session_state.jugadores.append({
                    "id": nuevo_id,
                    "nombre": nuevo_nombre.strip(),
                    "ligas": 0,
                    "copas": 0,
                    "descensos": 0
                })
                st.session_state.mensaje_exito_jugador = f"¡{nuevo_nombre.strip()} fue agregado con éxito!"
                st.rerun()

    # SECCIÓN DE ELIMINAR AMIGO
    with col_eliminar:
        st.markdown("### ❌ Eliminar Amigo")
        if not st.session_state.jugadores:
            st.info("No hay jugadores en la lista para eliminar.")
        else:
            lista_nombres_eliminar = [j["nombre"] for j in st.session_state.jugadores]
            jugador_a_eliminar = st.selectbox("Selecciona a quién dar de baja:", lista_nombres_eliminar)
            
            # Advertencia visual antes de cometer un error
            st.caption(f"⚠️ Al presionar el botón eliminarás permanentemente a **{jugador_a_eliminar}** y todo su registro.")
            
            if st.button("Eliminar Jugador ❌", type="secondary", use_container_width=True):
                # Filtramos la lista de jugadores removiendo al seleccionado
                st.session_state.jugadores = [j for j in st.session_state.jugadores if j["nombre"] != jugador_a_eliminar]
                st.session_state.mensaje_exito_jugador = f"¡{jugador_a_eliminar} ha sido dado de baja de la plantilla!"
                st.rerun()

# ----------------------------------------------------------------------------
# PESTAÑA 4: HISTORIAL DE TORNEOS
# ----------------------------------------------------------------------------
with tab_historial:
    st.header("📜 Historial de Competencias")
    
    if not st.session_state.torneos:
        st.info("Todavía no se registraron torneos en esta sesión web.")
    else:
        for idx, t in enumerate(reversed(st.session_state.torneos)):
            icon = "🏆" if t["tipo"] == "Liga" else "🥇"
            with st.expander(f"{icon} {t['nombre']} ({t['tipo']})"):
                st.write(f"**Ganador:** {t['campeon']}")
                st.write(f"**Último puesto:** {t['descenso']}")