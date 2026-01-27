import streamlit as st
from db import init_db, get_session
# Asegúrate de que tus modelos (User, etc.) estén importados desde donde los definas
# from models import User 

# Importaciones de tus módulos
from jugadores import mostrar_planilla, inscripcion_nueva, edicion_eliminacion
from eventos import cobros_camisetas
from reportes import caja_reportes, historial_jugador
from cantina import gestionar_productos, registrar_ventas
from perfiles import configurar_perfiles

# 1. CONFIGURACIÓN DE PÁGINA (ESTRICTAMENTE PRIMERO)
st.set_page_config(page_title="Municipal PA - Pro", layout="centered")

# 2. INICIALIZACIÓN CONTROLADA DE DB
if "db_initialized" not in st.session_state:
    try:
        init_db()
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"⚠️ Error de conexión con Neon: {e}")
        st.info("Revisa tus Secrets y que la base de datos en Neon esté activa.")
        st.stop()

# --- ESTADOS DE SESIÓN ---
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "font_size" not in st.session_state:
    st.session_state.font_size = "medium"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Aplicar Estilos
st.markdown(f"""
    <style>
    .main {{ font-size: {st.session_state.font_size}; }}
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if not st.session_state.logged_in:
    st.title("⚽ Municipal PA - Acceso")
    with st.form("login_form"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        
        if st.form_submit_button("Entrar"):
            try:
                # Importamos User aquí si es necesario para evitar importaciones circulares
                from db import User 
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
            except Exception as e:
                st.error("Error al conectar con la base de datos para el login.")
                st.exception(e)
                
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
    
    if st.button("Cerrar Sesión", use_container_width=True):
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
try:
    if menu == "📋 Planilla y Control Edad":
        mostrar_planilla()
    elif menu == "🏟️ Cobros y Camisetas":
        cobros_camisetas()
    elif menu == "👤 Inscripción Nueva":
        if st.session_state.role == 'admin':
            inscripcion_nueva()
        else:
            st.warning("Acceso restringido.")
    elif menu == "✏️ Edición y Eliminación":
        if st.session_state.role == 'admin':
            edicion_eliminacion()
        else:
            st.warning("Acceso restringido.")
    elif menu == "📊 Caja y Reportes":
        caja_reportes()
    elif menu == "📜 Historial por Jugador":
        historial_jugador()
    elif menu == "🔧 Configurar Perfiles":
        configurar_perfiles()
    elif menu == "🍻 Cantina":
        submenu = st.selectbox("Operación:", ["Registrar Venta", "Gestionar Productos"])
        if submenu == "Gestionar Productos":
            if st.session_state.role == 'admin': gestionar_productos()
            else: st.warning("Solo administradores.")
        else:
            registrar_ventas()
except Exception as e:
    st.error(f"Error en el módulo {menu}")
    st.exception(e)
