import streamlit as st
from db import init_db, get_session, User

# Importación segura de tus módulos
try:
    from jugadores import mostrar_planilla, inscripcion_nueva, edicion_eliminacion
    from reportes import caja_reportes
    # Agrega aquí tus otras importaciones (eventos, cantina, perfiles)
except ImportError:
    pass

st.set_page_config(page_title="Municipal PA - Pro", layout="wide")

# Inicialización de DB
if "db_initialized" not in st.session_state:
    try:
        init_db()
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"Error de conexión con Neon: {e}")
        st.stop()

# Manejo de Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("⚽ Acceso Municipal Puente Alto")
    with st.form("login"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            session = get_session()
            user = session.query(User).filter_by(username=u, password=p).first()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.role = user.role
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
            session.close()
    st.stop()

# Interfaz Principal
st.sidebar.title(f"Hola, {st.session_state.username}")
opcion = st.sidebar.radio("Menú", ["📋 Planilla", "📊 Reportes", "⚙️ Configuración"])

if st.sidebar.button("Salir"):
    st.session_state.logged_in = False
    st.rerun()

if opcion == "📋 Planilla":
    st.header("Gestión de Jugadores")
    # mostrar_planilla() 
elif opcion == "📊 Reportes":
    st.header("Reportes de Caja")
    # caja_reportes()
