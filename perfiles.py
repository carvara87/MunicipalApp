# perfiles.py
import streamlit as st
from db import get_session, User
import pandas as pd

def configurar_perfiles():
    st.subheader("Configuración de Perfiles")
    
    session = get_session()
    try:
        users = session.query(User).all()
        if users:
            df_u = pd.DataFrame([{
                'ID': u.id,
                'Username': u.username,
                'Role': u.role
            } for u in users])
            st.dataframe(df_u, use_container_width=True, hide_index=True)
        
        # Agregar nuevo usuario
        with st.form("nuevo_usuario"):
            username = st.text_input("Username")
            password = st.text_input("Contraseña", type="password")
            role = st.selectbox("Rol", ["viewer"])  # Solo viewer, admin solo manual
            if st.form_submit_button("Crear Usuario"):
                if username and password:
                    existe = session.query(User).filter_by(username=username).first()
                    if existe:
                        st.error("Username ya existe.")
                    else:
                        nuevo = User(username=username, password=password, role=role)
                        session.add(nuevo)
                        session.commit()
                        st.success("Usuario creado.")
                        st.rerun()
                else:
                    st.error("Campos requeridos.")
        
        # Editar/Eliminar
        if users:
            selected_id = st.selectbox("Seleccionar ID para editar/eliminar:", [u.id for u in users])
            user = session.query(User).filter_by(id=selected_id).first()
            if user and user.role != 'admin':  # No editar admin
                with st.form("editar_usuario"):
                    username = st.text_input("Username", value=user.username)
                    password = st.text_input("Nueva Contraseña (opcional)", type="password")
                    role = st.selectbox("Rol", ["viewer"], index=0)
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("Actualizar"):
                        if username != user.username:
                            existe = session.query(User).filter_by(username=username).first()
                            if existe:
                                st.error("Username ya existe.")
                                return
                        user.username = username
                        if password:
                            user.password = password
                        user.role = role
                        session.commit()
                        st.success("Usuario actualizado.")
                        st.rerun()
                    if col2.form_submit_button("Eliminar"):
                        session.delete(user)
                        session.commit()
                        st.success("Usuario eliminado.")
                        st.rerun()
            elif user.role == 'admin':
                st.info("No se puede editar el admin.")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        session.close()