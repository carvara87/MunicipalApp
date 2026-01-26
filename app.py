# app.py
import streamlit as st
from db import init_db, get_session, User
from jugadores import mostrar_planilla, inscripcion_nueva, edicion_eliminacion
from eventos import cobros_camisetas
from reportes import caja_reportes, historial_jugador
from cantina import gestionar_productos, registrar_ventas
from perfiles import configurar_perfiles

# 1. Inicializar la base de datos al arrancar
# Esto crea las tablas en Neon automáticamente si no existen
try:
    init_db()
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")

st.set_page_config(page_title="Municipal PA - Pro", layout="centered")

# --- ESTILOS PERSONALIZADOS ---
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "font_size" not in st.session_state:
    st.session_state.font_size = "medium"

# Aplicar CSS básico para el tema
st.markdown(f"""
    <style>
    .main {{ font-size: {st.session_state.font_size}; }}
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("⚽ Municipal PA - Acceso")
    with st.form("login_form"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            session = get_session()
            user = session.query(User).filter_by(username=user_input, password=pass_input).first()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.role = user.role
                session.close()
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
                session.close()
    st.info("Nota: Si es la primera vez, el usuario es 'admin' y la clave 'admin123'")
    st.stop()

# --- INTERFAZ PRINCIPAL (Solo si está logueado) ---
st.title(f"🏆 Municipal PA - {st.session_state.username.capitalize()}")

with st.sidebar:
    st.header("⚙️ Configuración")
    theme = st.selectbox("Tema", ["Claro", "Oscuro"], index=0 if st.session_state.theme == "light" else 1)
    st.session_state.theme = "light" if theme == "Claro" else "dark"
    
    font_size = st.selectbox("Tamaño de Fuente", ["Chico", "Mediano", "Grande"], index=1)
    st.session_state.font_size = {"Chico": "small", "Mediano": "medium", "Grande": "large"}[font_size]
    
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# --- MENÚ DE NAVEGACIÓN ---
menu_options = [
    "📋 Planilla y Control Edad", 
    "🏟️ Cobros y Camisetas", 
    "👤 Inscripción Nueva", 
    "✏️ Edición y Eliminación", 
    "📊 Caja y Reportes", 
    "📜 Historial por Jugador",
    "🍻 Cantina"
]

if st.session_state.role == 'admin':
    menu_options.append("🔧 Configurar Perfiles")

menu = st.selectbox("Seleccione una opción:", menu_options)

# --- LÓGICA DE MÓDULOS ---
if menu == "📋 Planilla y Control Edad":
    mostrar_planilla()

elif menu == "🏟️ Cobros y Camisetas":
    cobros_camisetas()

elif menu == "👤 Inscripción Nueva":
    if st.session_state.role == 'admin':
        inscripcion_nueva()
    else:
        st.warning("Acceso restringido: Solo administradores pueden inscribir.")

elif menu == "✏️ Edición y Eliminación":
    if st.session_state.role == 'admin':
        edicion_eliminacion()
    else:
        st.warning("Acceso restringido: Solo administradores pueden editar.")

elif menu == "📊 Caja y Reportes":
    caja_reportes()

elif menu == "📜 Historial por Jugador":
    historial_jugador()

elif menu == "🔧 Configurar Perfiles":
    configurar_perfiles()

elif menu == "🍻 Cantina":
    submenu = st.selectbox("Operación de Cantina:", ["Registrar Venta", "Gestionar Productos"])
    if submenu == "Gestionar Productos":
        if st.session_state.role == 'admin':
            gestionar_productos()
        else:
            st.warning("Solo administradores pueden gestionar stock.")
    else:
        registrar_ventas()