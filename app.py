import streamlit as st
from sqlalchemy import text
from db import get_engine

st.set_page_config(
    page_title="Municipal Puente Alto",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Municipalidad de Puente Alto")

st.write("Inicializando aplicación...")

# ⛑️ Protección total de arranque
try:
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    st.success("✅ Conexión a Neon establecida correctamente")

except Exception as e:
    st.error("❌ Error crítico al iniciar la aplicación")
    st.code(str(e))
    st.stop()

st.divider()
st.info("🚀 Aplicación levantada correctamente")
