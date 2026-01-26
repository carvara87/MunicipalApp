# jugadores.py
import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text
from db import get_session, Jugador
from utils import calcular_edad, formatear_rut, validar_rut
import re

def mostrar_planilla():
    """Muestra la planilla de jugadores con filtros por serie"""
    st.subheader("Gestión de Jugadores")
    
    session = get_session()
    try:
        jugadores = session.query(Jugador).all()
        
        if not jugadores:
            st.info("No hay jugadores inscritos aún.")
            return
            
        # Creamos DataFrame para visualización
        df_j = pd.DataFrame([{
            'id': j.id,
            'Nombre': j.nombre,
            'Edad': j.edad,
            'Serie': j.serie,
            'RUT': j.rut,
            'Nacionalidad': j.nacionalidad,
            'Email': j.email
        } for j in jugadores])
        
        t1, t2, t3 = st.tabs(["Todos", "Serie +45", "1ra y 2da"])
        
        with t1:
            st.dataframe(
                df_j[["Nombre", "Edad", "Serie", "RUT", "Nacionalidad", "Email"]].sort_values("Nombre"),  # Ordenado por nombre
                use_container_width=True,
                hide_index=True
            )
            st.metric("Total Socios", len(df_j))
            
        with t2:
            df_45 = df_j[df_j['Serie'] == "+45"].copy()
            if not df_45.empty:
                def highlight_age(row):
                    color = '#ffcccc' if row['Edad'] < 45 else ''
                    return [f'background-color: {color}' if col == 'Edad' else '' for col in row.index]
                
                st.markdown("⚠️ *Celda roja: No cumple 45 años todavía*")
                styled_df = df_45[["Nombre", "Edad", "RUT", "Nacionalidad", "Email"]].style.apply(highlight_age, axis=1)
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.info("Sin jugadores en la serie +45.")
                
        with t3:
            df_adultas = df_j[df_j['Serie'].isin(["1ra y 2da"])].sort_values("Nombre")
            st.dataframe(
                df_adultas[["Nombre", "Edad", "Nacionalidad", "Email"]],
                use_container_width=True,
                hide_index=True
            )
            
    except Exception as e:
        st.error(f"Error al cargar la planilla: {str(e)}")
    finally:
        session.close()


def inscripcion_nueva():
    """Formulario para inscribir un nuevo jugador"""
    st.subheader("Registro de Socio")
    
    with st.form("registro_nuevo_jugador", clear_on_submit=True):
        col1, col2 = st.columns([3, 2])
        
        with col1:
            nom = st.text_input("Nombre y Apellido", placeholder="Ej: Juan Pérez González")
            rut_input = st.text_input(
                "RUT", 
                placeholder="Ej: 12345678-9", 
                help="Ingrese RUT con o sin puntos/guion. Se formateará al guardar."
            )
        
        with col2:
            f_n = st.date_input(
                "Fecha de Nacimiento",
                value=date(1990, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
        
        nacionalidad = st.selectbox("Nacionalidad", ["Chilena", "Peruana", "Haitiana", "Colombiana", "Venezolana", "Otros"])
        email = st.text_input("Correo Electrónico", placeholder="ejemplo@correo.com")
        tel = st.text_input("Teléfono", placeholder="+569 1234 5678")
        
        submitted = st.form_submit_button("✅ GUARDAR JUGADOR", use_container_width=True, type="primary")
        
        if submitted:
            if not nom.strip() or not rut_input.strip():
                st.error("Nombre y RUT son campos obligatorios.")
                st.stop()
                
            rut_formateado = formatear_rut(rut_input)
            if not validar_rut(rut_formateado):
                st.error("El RUT ingresado no es válido. Verifique formato y dígito verificador.")
                st.stop()
                
            edad = calcular_edad(f_n)
            serie = "+45" if edad >= 45 else "1ra y 2da"
            
            session = get_session()
            try:
                # Verificar si ya existe un jugador con ese RUT
                existe = session.query(Jugador).filter_by(rut=rut_formateado).first()
                if existe:
                    st.warning(f"Ya existe un jugador registrado con RUT {rut_formateado}")
                    st.stop()
                    
                nuevo = Jugador(
                    nombre=nom.strip(),
                    rut=rut_formateado,
                    serie=serie,
                    fecha_nacimiento=f_n,
                    edad=edad,
                    telefono=tel.strip() or None,
                    nacionalidad=nacionalidad,
                    email=email.strip() or None
                )
                
                session.add(nuevo)
                session.commit()
                st.success(f"¡{nom.strip()} ha sido registrado correctamente!")
                st.rerun()
                
            except Exception as e:
                session.rollback()
                st.error(f"Error al guardar el jugador: {str(e)}")
            finally:
                session.close()


def edicion_eliminacion():
    """Interfaz para editar o eliminar jugadores existentes"""
    st.subheader("Edición y Eliminación de Jugadores")
    
    session = get_session()
    try:
        jugadores = session.query(Jugador).order_by(Jugador.nombre).all()
        
        if not jugadores:
            st.info("No hay jugadores para editar o eliminar.")
            return
            
        # Lista de nombres para selección
        opciones = [f"{j.nombre}  —  {j.rut}" for j in jugadores]
        seleccion = st.selectbox("Seleccionar jugador:", opciones)
        
        if seleccion:
            # Extraer nombre (antes del guión)
            nombre_seleccionado = seleccion.split("  —  ")[0]
            jugador = session.query(Jugador).filter_by(nombre=nombre_seleccionado).first()
            
            if not jugador:
                st.error("No se encontró el jugador seleccionado.")
                return
                
            with st.form("editar_jugador"):
                st.markdown(f"**Editando:** {jugador.nombre} ({jugador.rut})")
                
                nom = st.text_input("Nombre y Apellido", value=jugador.nombre)
                rut_input = st.text_input(
                    "RUT", 
                    value=jugador.rut, 
                    help="Ingrese RUT con o sin puntos/guion. Se formateará al guardar."
                )
                f_n = st.date_input("Fecha de Nacimiento", value=jugador.fecha_nacimiento)
                nacionalidad = st.selectbox("Nacionalidad", ["Chilena", "Peruana", "Haitiana", "Colombiana", "Venezolana", "Otros"], index=["Chilena", "Peruana", "Haitiana", "Colombiana", "Venezolana", "Otros"].index(jugador.nacionalidad))
                email = st.text_input("Correo Electrónico", value=jugador.email or "")
                tel = st.text_input("Teléfono", value=jugador.telefono or "")
                
                col1, col2 = st.columns(2)
                
                update_submitted = col1.form_submit_button("✏️ Actualizar", type="primary")
                delete_submitted = col2.form_submit_button("🗑️ Eliminar", type="secondary")
                
                if update_submitted:
                    rut_formateado = formatear_rut(rut_input)
                    if not validar_rut(rut_formateado):
                        st.error("RUT inválido.")
                        st.stop()
                        
                    edad = calcular_edad(f_n)
                    serie = "+45" if edad >= 45 else "1ra y 2da"
                    
                    # Verificar duplicado RUT si cambiado
                    if rut_formateado != jugador.rut:
                        existe = session.query(Jugador).filter_by(rut=rut_formateado).first()
                        if existe:
                            st.error("Este RUT ya está registrado.")
                            st.stop()
                    
                    jugador.nombre = nom.strip()
                    jugador.rut = rut_formateado
                    jugador.serie = serie
                    jugador.fecha_nacimiento = f_n
                    jugador.edad = edad
                    jugador.telefono = tel.strip() or None
                    jugador.nacionalidad = nacionalidad
                    jugador.email = email.strip() or None
                    
                    session.commit()
                    st.success("Jugador actualizado correctamente")
                    st.rerun()
                
                if delete_submitted:
                    if st.session_state.get("confirm_delete", False):
                        session.delete(jugador)
                        session.commit()
                        st.success("Jugador eliminado permanentemente")
                        st.session_state.confirm_delete = False
                        st.rerun()
                    else:
                        st.session_state.confirm_delete = True
                        st.warning("¿Realmente deseas ELIMINAR este jugador? Presiona 'Eliminar' nuevamente para confirmar.")
                        
    except Exception as e:
        st.error(f"Error en edición/eliminación: {str(e)}")
    finally:
        session.close()