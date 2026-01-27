import streamlit as st
from sqlalchemy import text
from db import get_engine

# ---------- CONFIG STREAMLIT ----------
st.set_page_config(
    page_title="Municipal Puente Alto",
    page_icon="🏛️",
    layout="wide"
)

# ---------- UI ----------
st.title("🏛️ Municipalidad de Puente Alto")
st.write("Sistema conectado a base de datos Neon PostgreSQL")

# ---------- CONEXIÓN DB ----------
try:
    engine = get_engine()

    # Test real de conexión
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    st.success("✅ Conectado correctamente a la base de datos")

except Exception as e:
    st.error("❌ Error al conectar a la base de datos")
    st.code(str(e))
    st.stop()

# ---------- CONTENIDO DE PRUEBA ----------
st.divider()
st.subheader("Estado del sistema")
st.info("La aplicación está levantada y estable 🚀")
