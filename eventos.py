# eventos.py
import streamlit as st
from datetime import date, timedelta
from db import get_session, Evento, Pago, Jugador
from utils import formato_fecha_es
import pandas as pd

def cobros_camisetas():
    st.subheader("Control Post-Partido")
    fecha_inicio = date(2026, 1, 18)
    fecha_fin = date(2026, 12, 27)
    domingos = []
    curr = fecha_inicio
    while curr <= fecha_fin:
        domingos.append(curr)
        curr += timedelta(days=7)
    hoy = date.today()
    idx_default = next((i for i, d in enumerate(domingos) if d >= hoy), 0)
    f_sel = st.selectbox("Seleccionar Domingo:", domingos, index=idx_default, format_func=formato_fecha_es)
    f_str = f_sel.strftime("%Y-%m-%d")
    session = get_session()
    try:
        evento = session.query(Evento).filter_by(fecha=f_str).first()
        if not evento:
            rival = st.text_input("Equipo Rival:", placeholder="Ej: Defensor PA")
            cuota_default = st.number_input("Cuota Default por Jugador ($):", min_value=0, value=5000)
            if st.button("Crear Evento"):
                if not rival:
                    st.error("Rival requerido.")
                    return
                nuevo_evento = Evento(fecha=f_str, rival=rival, cuota_default=cuota_default)
                session.add(nuevo_evento)
                session.commit()
                st.success("Evento creado exitosamente.")
                st.rerun()
        else:
            rival = evento.rival
            cuota_default = evento.cuota_default
            st.write(f"🆚 Rival: {rival}")
            st.write(f"💰 Cuota Default: ${cuota_default:,}")
            st.divider()
            busc = st.text_input("🔍 Buscar Jugador:", "").lower()
            jugadores = session.query(Jugador).order_by(Jugador.nombre).all()  # Ordenado por nombre para mejor UX
            if not jugadores:
                st.warning("Inscriba jugadores primero.")
                return
            for j in jugadores:
                if busc in j.nombre.lower():
                    pago = session.query(Pago).filter_by(fecha=f_str, nombre=j.nombre).first()
                    with st.expander(f"**{j.nombre}** ({j.serie} | {j.edad} años)"):  # Usar expander para mejor organización
                        if pago:
                            falta = pago.cuota - pago.pagado
                            col = "green" if pago.estado == "Pagado" else "red" if pago.estado == "No Pagado" else "orange"
                            st.markdown(f"👕 N°**{pago.n_camiseta}** | :{col}[{pago.estado}] (Pagado: ${pago.pagado:,} / Falta: ${falta:,})")
                            if pago.estado != "Pagado":
                                max_abono = pago.cuota - pago.pagado
                                abono = st.number_input("Abono adicional ($)", min_value=0, max_value=max_abono, value=0, key=f"ab{j.id}")
                                if st.button("Agregar Abono", key=f"ab_b{j.id}"):
                                    if abono > 0:
                                        pago.pagado += abono
                                        pago.estado = "Pagado" if pago.pagado >= pago.cuota else "Pendiente"
                                        session.commit()
                                        st.success(f"Abono de ${abono:,} agregado.")
                                        st.rerun()
                                    else:
                                        st.warning("El abono debe ser mayor a 0.")
                        else:
                            cam = st.number_input("N° Cam", 1, 120, key=f"c{j.id}", value=None, placeholder="--")
                            cuota = st.number_input("Cuota ($)", 0, 20000, key=f"cu{j.id}", value=cuota_default)
                            pag = st.number_input("Pagado ($)", 0, 20000, key=f"p{j.id}", value=0)
                            if pag > cuota:
                                st.error("Pagado no puede exceder la cuota.")
                                return
                            b1, b2, b3 = st.columns(3)
                            if b1.button("PAGÓ", key=f"pa{j.id}"):
                                if not cam:
                                    st.error("N° Camiseta requerido.")
                                    return
                                estado = "Pagado" if pag >= cuota else "Pendiente"
                                nuevo_pago = Pago(fecha=f_str, rival=rival, nombre=j.nombre, serie=j.serie, n_camiseta=cam, cuota=cuota, pagado=pag, estado=estado)
                                session.add(nuevo_pago)
                                session.commit()
                                st.success("Pago registrado.")
                                st.rerun()
                            if b2.button("PENDIENTE", key=f"pe{j.id}"):
                                if not cam:
                                    st.error("N° Camiseta requerido.")
                                    return
                                nuevo_pago = Pago(fecha=f_str, rival=rival, nombre=j.nombre, serie=j.serie, n_camiseta=cam, cuota=cuota, pagado=pag, estado="Pendiente")
                                session.add(nuevo_pago)
                                session.commit()
                                st.success("Pago pendiente registrado.")
                                st.rerun()
                            if b3.button("NO PAGÓ", key=f"np{j.id}"):
                                if not cam:
                                    st.error("N° Camiseta requerido.")
                                    return
                                nuevo_pago = Pago(fecha=f_str, rival=rival, nombre=j.nombre, serie=j.serie, n_camiseta=cam, cuota=cuota, pagado=0, estado="No Pagado")
                                session.add(nuevo_pago)
                                session.commit()
                                st.success("No pago registrado.")
                                st.rerun()
    except Exception as e:
        session.rollback()
        st.error(f"Error: {e}")
    finally:
        session.close()