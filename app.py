import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA WEB Y ESTILOS VISUALES
# ============================================================================
st.set_page_config(
    page_title="FIFA Stats Tracker",
    page_icon="⚽",
    layout="centered"
)

st.markdown("""
    <style>
        html, body, [class*="css"] { font-size: 1.1rem !important; }
        h1 { font-size: 3rem !important; font-weight: 800 !important; }
        h2 { font-size: 2rem !important; font-weight: 700 !important; }
        h3 { font-size: 1.5rem !important; }
        .stTabs [data-baseweb="tab"] { font-size: 1.25rem !important; font-weight: bold !important; padding: 10px 20px !important; }
        div.stButton > button { font-size: 1.1rem !important; padding: 0.5rem 1rem !important; border-radius: 8px !important; }
        .metric-card { background-color: rgba(250, 250, 250, 0.1); border: 1px solid rgba(128, 128, 128, 0.2); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CONTROLADOR DE BASE DE DATOS (GOOGLE SHEETS)
# ============================================================================

# Verificar si las credenciales secretas están configuradas en Streamlit Cloud
if "gcp_service_account" not in st.secrets or "spreadsheet_key" not in st.secrets:
    st.markdown("<h1 style='text-align: center;'>⚽ FIFA Stats Tracker</h1>", unsafe_allow_html=True)
    st.info("👋 ¡Tu aplicación ya está en la nube! Ahora falta conectar tu base de datos de Google Sheets.")
    
    st.markdown("""
    ### 🛠️ Pasos para activar el guardado permanente:
    1. **Creá una planilla de Google Sheets** en tu Google Drive.
    2. **Creá un proyecto en Google Cloud Console**, activá las APIs de *Google Drive* y *Google Sheets*, y creá una **Cuenta de Servicio** (Service Account) para obtener un archivo de clave `.json`.
    3. **Compartí tu planilla de Google Sheets** dándole permisos de 'Editor' al correo largo de tu Cuenta de Servicio.
    4. **Cargá los secretos en Streamlit Cloud**: Ve al panel de control de tu app en Streamlit, entra a **Settings ⚙️ -> Secrets** y pega la configuración de esta manera:
    
    ```toml
    spreadsheet_key = "TU_ID_DE_PLANILLA_DE_GOOGLE_SHEETS"

    [gcp_service_account]
    type = "service_account"
    project_id = "tu-proyecto"
    private_key_id = "..."
    private_key = "-----BEGIN PRIVATE KEY-----\\n..."
    client_email = "..."
    # ... (copia y pega todas las líneas que vengan dentro de tu archivo JSON descargado)
    ```
    5. ¡Actualizá esta página y listo! Tu torneo tendrá memoria eterna.
    """)
    st.stop() # Frena la ejecución limpia aquí hasta que se configuren los secretos

# Si las credenciales existen, nos conectamos de forma segura
@st.cache_resource
def conectar_base_de_datos():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(st.secrets["spreadsheet_key"])

try:
    spreadsheet = conectar_base_de_datos()
    # Aseguramos que existan las dos pestañas en el Excel, si no, las crea
    try:
        ws_jugadores = spreadsheet.worksheet("jugadores")
    except gspread.exceptions.WorksheetNotFound:
        ws_jugadores = spreadsheet.add_worksheet(title="jugadores", rows="100", cols="5")
        ws_jugadores.append_row(["id", "nombre", "ligas", "copas", "descensos"])

    try:
        ws_torneos = spreadsheet.worksheet("torneos")
    except gspread.exceptions.WorksheetNotFound:
        ws_torneos = spreadsheet.add_worksheet(title="torneos", rows="500", cols="4")
        ws_torneos.append_row(["nombre", "tipo", "campeon", "descenso"])
except Exception as e:
    st.error(f"Error de conexión con Google Sheets: {e}")
    st.stop()

# --- Funciones de sincronización ---
def descargar_datos_desde_sheets():
    # Cargar Jugadores
    filas_j = ws_jugadores.get_all_records()
    st.session_state.jugadores = []
    for f in filas_j:
        st.session_state.jugadores.append({
            "id": int(f["id"]),
            "nombre": str(f["nombre"]),
            "ligas": int(f["ligas"]),
            "copas": int(f["copas"]),
            "descensos": int(f["descensos"])
        })
    # Cargar Torneos
    filas_t = ws_torneos.get_all_records()
    st.session_state.torneos = []
    for f in filas_t:
        st.session_state.torneos.append({
            "nombre": str(f["nombre"]),
            "tipo": str(f["tipo"]),
            "campeon": str(f["campeon"]),
            "descenso": str(f["descenso"])
        })

def guardar_jugadores_en_sheets():
    # Limpiamos el contenido viejo (excepto la cabecera) y sobreescribimos todo para evitar duplicados
    ws_jugadores.clear()
    ws_jugadores.append_row(["id", "nombre", "ligas", "copas", "descensos"])
    for j in st.session_state.jugadores:
        ws_jugadores.append_row([j["id"], j["nombre"], j["ligas"], j["copas"], j["descensos"]])

def registrar_torneo_en_sheets(nuevo_torneo):
    ws_torneos.append_row([nuevo_torneo["nombre"], nuevo_torneo["tipo"], nuevo_torneo["campeon"], nuevo_torneo["descenso"]])


# ============================================================================
# INICIALIZACIÓN DE MEMORIA CACHÉ
# ============================================================================
if "base_sincronizada" not in st.session_state:
    descargar_datos_desde_sheets()
    st.session_state.base_sincronizada = True

if "mensaje_exito_jugador" not in st.session_state: st.session_state.mensaje_exito_jugador = None
if "mensaje_exito_torneo" not in st.session_state: st.session_state.mensaje_exito_torneo = None
if "mensaje_error_jugador" not in st.session_state: st.session_state.mensaje_error_jugador = None
if "lanzar_globos" not in st.session_state: st.session_state.lanzar_globos = False

if st.session_state.lanzar_globos:
    st.balloons()
    st.session_state.lanzar_globos = False

# ============================================================================
# ESTRUCTURA VISUAL PRINCIPAL
# ============================================================================
st.markdown("<h1 style='text-align: center;'>⚽ FIFA Stats Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.25rem; color: gray;'>¡Control de estadísticas guardado permanentemente en la nube!</p>", unsafe_allow_html=True)
st.markdown("---")

tab_ranking, tab_torneo, tab_amigos, tab_historial = st.tabs([
    "🏆 Salón de la Fama", 
    "🔥 Registrar Torneo", 
    "👥 Amigos", 
    "📜 Historial"
])

# ----------------------------------------------------------------------------
# PESTAÑA 1: SALÓN DE LA FAMA
# ----------------------------------------------------------------------------
with tab_ranking:
    if not st.session_state.jugadores:
        st.info("👋 ¡Bienvenido! Registra a tus amigos en la pestaña 👥 Amigos para empezar a sumar estadísticas.")
    else:
        st.markdown("### 🔥 Destacados de la Temporada")
        col_rey, col_sotano = st.columns(2)
        
        rey_nombre, rey_titulos = "Nadie aún", 0
        for j in st.session_state.jugadores:
            tot = j["ligas"] + j["copas"]
            if tot > rey_titulos:
                rey_titulos = tot
                rey_nombre = j["nombre"]
            elif tot == rey_titulos and rey_titulos > 0:
                if j["nombre"] not in rey_nombre: rey_nombre += f", {j['nombre']}"
        
        victima_nombre, max_descensos = "Nadie aún", 0
        for j in st.session_state.jugadores:
            desc = j["descensos"]
            if desc > max_descensos:
                max_descensos = desc
                victima_nombre = j["nombre"]
            elif desc == max_descensos and max_descensos > 0:
                if j["nombre"] not in victima_nombre: victima_nombre += f", {j['nombre']}"

        with col_rey:
            st.markdown(f'<div class="metric-card" style="border-top: 5px solid #FFD700;"><span style="font-size: 2.2rem;">👑</span><h4 style="margin: 5px 0; color: #FFD700; font-size: 1.2rem;">REY DE COPAS</h4><p style="font-size: 1.6rem; font-weight: bold; margin: 0;">{rey_nombre}</p><small style="color: gray;">{rey_titulos} título(s) total(es)</small></div>', unsafe_allow_html=True)
        with col_sotano:
            st.markdown(f'<div class="metric-card" style="border-top: 5px solid #FF4B4B;"><span style="font-size: 2.2rem;">💀</span><h4 style="margin: 5px 0; color: #FF4B4B; font-size: 1.2rem;">SÓTANO DE LA TABLA</h4><p style="font-size: 1.6rem; font-weight: bold; margin: 0;">{victima_nombre}</p><small style="color: gray;">{max_descensos} descenso(s)</small></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🏆 Tabla General de Posiciones")
        df = pd.DataFrame(st.session_state.jugadores)
        df["Total ⭐"] = df["ligas"] + df["copas"]
        df = df.rename(columns={"nombre": "Crack", "ligas": "Ligas 🏆", "copas": "Copas 🥇", "descensos": "Descensos 💀"})
        df = df.sort_values(by=["Total ⭐", "Ligas 🏆", "Descensos 💀"], ascending=[False, False, True])
        df.index = range(1, len(df) + 1)
        st.dataframe(df[["Crack", "Total ⭐", "Ligas 🏆", "Copas 🥇", "Descensos 💀"]], use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚙️ Ajuste de Puntos Manual (Suma / Resta Rápida)"):
            lista_nombres_ajuste = [j["nombre"] for j in st.session_state.jugadores]
            col_jug, col_stat, col_btn = st.columns([2, 2, 1.5])
            with col_jug: jugador_a_ajustar = st.selectbox("Selecciona un amigo:", lista_nombres_ajuste, key="sb_ajuste_jugador")
            with col_stat: stat_a_ajustar = st.selectbox("Estadística a modificar:", ["Ligas", "Copas", "Descensos"], key="sb_ajuste_stat")
            with col_btn:
                st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                sub_col1, sub_col2 = st.columns(2)
                referencia_jugador = next(j for j in st.session_state.jugadores if j["nombre"] == jugador_a_ajustar)
                clave = "ligas" if stat_a_ajustar == "Ligas" else ("copas" if stat_a_ajustar == "Copas" else "descensos")
                
                with sub_col1:
                    if st.button("➖", key="btn_restar_stat"):
                        referencia_jugador[clave] = max(0, referencia_jugador[clave] - 1)
                        guardar_jugadores_en_sheets() # Sincroniza al Excel
                        st.rerun()
                with sub_col2:
                    if st.button("➕", key="btn_sumar_stat"):
                        referencia_jugador[clave] += 1
                        guardar_jugadores_en_sheets() # Sincroniza al Excel
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
                if posibles_descendidos: descendido_nombre = st.selectbox("💀 ¿Quién quedó último?", posibles_descendidos)

            if st.button("Guardar Torneo 💾", type="primary"):
                if not nombre_torneo.strip():
                    st.error("Por favor, ingresá un nombre para el torneo.")
                else:
                    for j in st.session_state.jugadores:
                        if j["nombre"] == campeon_nombre:
                            if tipo_torneo == "Liga": j["ligas"] += 1
                            else: j["copas"] += 1
                        if hubo_descenso and j["nombre"] == descendido_nombre: j["descensos"] += 1
                    
                    nuevo_torneo = {
                        "nombre": nombre_torneo, "tipo": tipo_torneo,
                        "campeon": campeon_nombre, "descenso": descendido_nombre if hubo_descenso else "Ninguno"
                    }
                    
                    # Sincronización Doble en la Base de Datos
                    registrar_torneo_en_sheets(nuevo_torneo)
                    guardar_jugadores_en_sheets()
                    
                    st.session_state.mensaje_exito_torneo = f"¡Torneo '{nombre_torneo}' guardado permanentemente!"
                    st.session_state.lanzar_globos = True
                    descargar_datos_desde_sheets() # Recarga limpia
                    st.rerun()

# ----------------------------------------------------------------------------
# PESTAÑA 3: GESTIÓN DE AMIGOS
# ----------------------------------------------------------------------------
with tab_amigos:
    st.header("👥 Gestión de Plantilla de Amigos")
    if st.session_state.mensaje_exito_jugador:
        st.success(st.session_state.mensaje_exito_jugador)
        st.session_state.mensaje_exito_jugador = None
    if st.session_state.mensaje_error_jugador:
        st.error(st.session_state.mensaje_error_jugador)
        st.session_state.mensaje_error_jugador = None

    col_agregar, col_eliminar = st.columns(2)
    with col_agregar:
        st.markdown("### 👤 Añadir Amigo")
        nuevo_nombre = st.text_input("Nombre del nuevo integrante:", placeholder="Ej: Marcos", key="input_nuevo_nombre")
        if st.button("Fichar Jugador 📝", use_container_width=True):
            if not nuevo_nombre.strip():
                st.session_state.mensaje_error_jugador = "El nombre no puede estar vacío."
                st.rerun()
            elif nuevo_nombre.strip() in [j["nombre"] for j in st.session_state.jugadores]:
                st.session_state.mensaje_error_jugador = f"¡El jugador {nuevo_nombre.strip()} ya existe!"
                st.rerun()
            else:
                nuevo_id = max([j["id"] for j in st.session_state.jugadores], default=0) + 1
                st.session_state.jugadores.append({"id": nuevo_id, "nombre": nuevo_nombre.strip(), "ligas": 0, "copas": 0, "descensos": 0})
                guardar_jugadores_en_sheets() # Sincroniza al Excel
                st.session_state.mensaje_exito_jugador = f"¡{nuevo_nombre.strip()} guardado en la base de datos!"
                st.rerun()

    with col_eliminar:
        st.markdown("### ❌ Eliminar Amigo")
        if not st.session_state.jugadores:
            st.info("No hay jugadores para eliminar.")
        else:
            lista_nombres_eliminar = [j["nombre"] for j in st.session_state.jugadores]
            jugador_a_eliminar = st.selectbox("Selecciona a quién dar de baja:", lista_nombres_eliminar)
            st.caption(f"⚠️ Se eliminará a **{jugador_a_eliminar}** del Excel permanente.")
            if st.button("Eliminar Jugador ❌", type="secondary", use_container_width=True):
                st.session_state.jugadores = [j for j in st.session_state.jugadores if j["nombre"] != jugador_a_eliminar]
                guardar_jugadores_en_sheets() # Sincroniza al Excel removiendo la fila
                st.session_state.mensaje_exito_jugador = f"¡{jugador_a_eliminar} ha sido dado de baja!"
                st.rerun()

# ----------------------------------------------------------------------------
# PESTAÑA 4: HISTORIAL DE TORNEOS
# ----------------------------------------------------------------------------
with tab_historial:
    st.header("📜 Historial de Competencias")
    if not st.session_state.torneos:
        st.info("No hay torneos registrados en el historial del Excel.")
    else:
        for idx, t in enumerate(reversed(st.session_state.torneos)):
            icon = "🏆" if t["tipo"] == "Liga" else "🥇"
            with st.expander(f"{icon} {t['nombre']} ({t['tipo']})"):
                st.write(f"**Ganador:** {t['campeon']}")
                st.write(f"**Último puesto:** {t['descenso']}")
