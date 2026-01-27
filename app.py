import streamlit as st
from db import init_db, get_session, User

# Importación de tus otros módulos
try:
    from jugadores import mostrar_planilla
    # Agrega tus otros módulos aquí
except ImportError:
    pass

st.set_page_config(page_title="Municipal PA - Pro", layout="wide")

# Inicialización controlada para no bloquear el inicio
if "db_ready" not in st.session_state:
    try:
        init_db()
        st.session_state.db_ready = True
    except Exception as e:
        st.error("Despertando base de datos... Por favor espera 10 segundos y recarga.")
        st.stop()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("⚽ Municipal Puente Alto")
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            session = get_session()
            user = session.query(User).filter_by(username=u, password=p).first()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.role = user.role
                session.close()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
                session.close()
    st.stop()

# Menú Principal
st.sidebar.title(f"Usuario: {st.session_state.username}")
menu = st.sidebar.radio("Navegación", ["📋 Planilla", "📊 Reportes"])

if st.sidebar.button("Salir"):
    st.session_state.logged_in = False
    st.rerun()

if menu == "📋 Planilla":
    st.header("Planilla de Jugadores")
    # mostrar_planilla()
