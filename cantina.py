# cantina.py (modified)
# cantina.py
import streamlit as st
from db import get_session, Producto, Venta, Jugador  # Added Jugador import
from datetime import date
import pandas as pd

def gestionar_productos():
    st.subheader("Gestión de Productos")
    
    session = get_session()
    try:
        productos = session.query(Producto).all()
        
        if not productos:
            st.info("No hay productos aún.")
        else:
            df_p = pd.DataFrame([{
                'ID': p.id,
                'Nombre': p.nombre,
                'Tipo': p.tipo,
                'Precio': p.precio
            } for p in productos])
            st.dataframe(df_p, use_container_width=True, hide_index=True)
        
        # Agregar nuevo
        with st.form("nuevo_producto"):
            nombre = st.text_input("Nombre")
            tipo = st.selectbox("Tipo", ["Bebida", "Cerveza", "Comida"])
            precio = st.number_input("Precio", min_value=0.0)
            if st.form_submit_button("Agregar"):
                if nombre:
                    nuevo = Producto(nombre=nombre, tipo=tipo, precio=precio)
                    session.add(nuevo)
                    session.commit()
                    st.success("Producto agregado.")
                    st.rerun()
                else:
                    st.error("Nombre requerido.")
        
        # Editar/Eliminar
        if productos:
            selected_id = st.selectbox("Seleccionar ID para editar/eliminar:", [p.id for p in productos])
            prod = session.query(Producto).filter_by(id=selected_id).first()
            if prod:
                with st.form("editar_producto"):
                    nombre = st.text_input("Nombre", value=prod.nombre)
                    tipo = st.selectbox("Tipo", ["Bebida", "Cerveza", "Comida"], index=["Bebida", "Cerveza", "Comida"].index(prod.tipo))
                    precio = st.number_input("Precio", value=prod.precio)
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("Actualizar"):
                        prod.nombre = nombre
                        prod.tipo = tipo
                        prod.precio = precio
                        session.commit()
                        st.success("Producto actualizado.")
                        st.rerun()
                    if col2.form_submit_button("Eliminar"):
                        session.delete(prod)
                        session.commit()
                        st.success("Producto eliminado.")
                        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        session.close()

def registrar_ventas():
    st.subheader("Registro de Ventas")
    
    session = get_session()
    try:
        productos = session.query(Producto).all()
        if not productos:
            st.warning("Agregue productos primero.")
            return
        
        jugadores = session.query(Jugador).order_by(Jugador.nombre).all()
        if not jugadores:
            st.warning("Agregue jugadores primero.")
            return
        
        with st.form("nueva_venta"):
            # Nueva selección de jugador
            jugador_options = [f"{j.id} - {j.nombre} ({j.serie})" for j in jugadores]
            selected_jugador = st.selectbox("Asociar venta a Jugador:", jugador_options)
            jugador_id = int(selected_jugador.split(" - ")[0])
            
            producto_id = st.selectbox("Producto:", [f"{p.id} - {p.nombre} (${p.precio})" for p in productos])
            producto_id = int(producto_id.split(" - ")[0])
            cantidad = st.number_input("Cantidad", min_value=1)
            prod = session.query(Producto).filter_by(id=producto_id).first()
            total = prod.precio * cantidad
            st.write(f"Total: ${total}")
            if st.form_submit_button("Registrar Venta"):
                nueva_venta = Venta(
                    fecha=date.today(),
                    producto_id=producto_id,
                    cantidad=cantidad,
                    total=total,
                    jugador_id=jugador_id  # Asociar al jugador
                )
                session.add(nueva_venta)
                session.commit()
                st.success(f"Venta registrada y asociada a {selected_jugador.split(' - ')[1]}.")
        
        # Mostrar ventas con detalle de jugador
        ventas = session.query(Venta).all()
        if ventas:
            df_v = pd.DataFrame([{
                'ID': v.id,
                'Fecha': v.fecha,
                'Jugador ID': v.jugador_id,
                'Jugador Nombre': session.query(Jugador).filter_by(id=v.jugador_id).first().nombre if v.jugador_id else 'No Asociado',
                'Producto ID': v.producto_id,
                'Producto Nombre': session.query(Producto).filter_by(id=v.producto_id).first().nombre,
                'Cantidad': v.cantidad,
                'Total': v.total
            } for v in ventas])
            st.dataframe(df_v, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        session.close()