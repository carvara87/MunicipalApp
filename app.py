import streamlit as st
from db import init_db, get_session, User

# Importación de módulos externos (asegúrate de que existan en tu repo)
try:
    from jugadores import mostrar_planilla, inscripcion_nueva, edicion_eliminacion
    from eventos import cobros_camisetas
    from reportes import caja_reportes, historial_jugador
    from cantina import gestionar_productos, registrar_ventas
    from perfiles import configurar_perfiles
except ImportError as e:
    st.error(f"Error al importar módulos: {e}")

# 1. Configuración de página - SIEMPRE PRIMERO
st.set_page_config(page_title="Municipal PA - Pro", layout="wide", page_icon="⚽")

# 2. Inicialización de DB controlada por caché de sesión
if "db_ready" not in st.session_state:
    with st.spinner("Conectando con la base de datos municipal..."):
        try:
            init_db()
            st.session_state.db_ready = True
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            st.stop()

# --- Control de Acceso ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("⚽ Municipal Puente Alto - Acceso")
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            db = get_session()
            user = db.query(User).filter_by(username=u, password=p).first()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.role = user.role
                db.close()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
                db.close()
    st.stop()

# --- Interfaz de Usuario Logueado ---
st.sidebar.title(f"Bienvenido, {st.session_state.username}")
menu = st.sidebar.radio("Navegación", [
    "📋 Planilla", "🏟️ Cobros", "👤 Inscripción", 
    "✏️ Editar", "📊 Reportes", "🍻 Cantina", "🔧 Ajustes"
])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.logged_in = False
    st.rerun()

# --- Renderizado de Módulos ---
try:
    if menu == "📋 Planilla": mostrar_planilla()
    elif menu == "🏟️ Cobros": cobros_camisetas()
    elif menu == "👤 Inscripción": inscripcion_nueva() if st.session_state.role == 'admin' else st.warning("Solo Admin")
    elif menu == "✏️ Editar": edicion_eliminacion() if st.session_state.role == 'admin' else st.warning("Solo Admin")
    elif menu == "📊 Reportes": caja_reportes()
    elif menu == "🍻 Cantina": registrar_ventas()
    elif menu == "🔧 Ajustes": configurar_perfiles() if st.session_state.role == 'admin' else st.warning("Solo Admin")
except NameError:
    st.info("El módulo seleccionado aún no está disponible.")
