# reportes.py (modified)
# reportes.py
import streamlit as st
from db import get_session, Pago, Evento, Jugador, Venta, Producto  # Added Venta and Producto imports
from utils import MESES_ES
import pandas as pd
from datetime import date, datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def caja_reportes():
    st.subheader("Resumen de Finanzas")
    session = get_session()
    try:
        pagos = session.query(Pago).all()
        if not pagos:
            st.info("No hay pagos registrados.")
            return
        df_p = pd.DataFrame([{
            'fecha': p.fecha, 'rival': p.rival, 'nombre': p.nombre, 'serie': p.serie,
            'n_camiseta': p.n_camiseta, 'cuota': p.cuota, 'pagado': p.pagado, 'estado': p.estado
        } for p in pagos])
        total_p = df_p['pagado'].sum()
        total_d = df_p[df_p['estado'].isin(['Pendiente', 'No Pagado'])]['cuota'].sum() - df_p[df_p['estado'] == 'Pendiente']['pagado'].sum()
        c1, c2 = st.columns(2)
        c1.metric("En Caja (Cuotas)", f"${total_p:,}")
        c2.metric("Por Cobrar (Cuotas)", f"${total_d:,}", delta_color="inverse")
        
        # Calcular total general de cantina (todas las ventas)
        ventas = session.query(Venta).all()
        df_v = pd.DataFrame([{
            'fecha': v.fecha.isoformat(),  # Convertir Date a string YYYY-MM-DD para consistencia
            'jugador_id': v.jugador_id,
            'producto_id': v.producto_id,
            'cantidad': v.cantidad,
            'total': v.total
        } for v in ventas])
        total_cantina_global = df_v['total'].sum()
        st.metric("En Caja (Cantina Total)", f"${total_cantina_global:,}")
        
        st.divider()
        eventos = session.query(Evento).all()
        fechas_disp = sorted([e.fecha for e in eventos], reverse=True)
        f_rep_str = st.selectbox("Elegir Fecha para Informe:", fechas_disp)
        if f_rep_str:
            df_rep = df_p[df_p['fecha'] == f_rep_str]
            d_obj = datetime.strptime(f_rep_str, "%Y-%m-%d").date()
            fecha_es = f"{d_obj.day} de {MESES_ES[d_obj.month]}"
            
            # Filtrar ventas de cantina para esta fecha específica
            df_v_evento = df_v[df_v['fecha'] == f_rep_str]
            total_cantina_evento = df_v_evento['total'].sum()
            
            # Total general para el evento (cuotas pagadas + cantina)
            total_general_evento = df_rep['pagado'].sum() + total_cantina_evento
            
            resumen = f"*MUNICIPAL PUENTE ALTO*\n"
            resumen += f"📅 Fecha: {fecha_es}\n"
            rival = df_rep['rival'].iloc[0] if not df_rep.empty else ''
            resumen += f"🆚 Rival: {rival}\n"
            resumen += f"💰 Recaudado Cuotas: ${df_rep['pagado'].sum():,}\n"
            resumen += f"🍻 Recaudado Cantina: ${total_cantina_evento:,}\n"
            resumen += f"📈 Total General: ${total_general_evento:,}\n"
            
            pendientes = df_rep[df_rep['estado'].isin(['Pendiente', 'No Pagado'])]
            if not pendientes.empty:
                resumen += "\n⚠️ *PENDIENTES / NO PAGADOS (CUOTAS):* \n"
                for _, d in pendientes.iterrows():
                    falta = d['cuota'] - d['pagado']
                    estado_det = f"{d['estado']} (Falta: ${falta:,})"
                    resumen += f"- {d['nombre']} ({estado_det})\n"
            
            # Detalle sofisticado de ventas en cantina por evento
            if not df_v_evento.empty:
                resumen += "\n🍻 *DETALLE VENTAS CANTINA:* \n"
                grouped_ventas = df_v_evento.groupby(['jugador_id', 'producto_id']).agg({'cantidad': 'sum', 'total': 'sum'}).reset_index()
                for _, v in grouped_ventas.iterrows():
                    jugador_nombre = session.query(Jugador).filter_by(id=v['jugador_id']).first().nombre if v['jugador_id'] else 'No Asociado'
                    producto_nombre = session.query(Producto).filter_by(id=v['producto_id']).first().nombre
                    resumen += f"- {jugador_nombre}: {producto_nombre} (Cant: {v['cantidad']}, Total: ${v['total']:,})\n"
            else:
                resumen += "\n🍻 *DETALLE VENTAS CANTINA:* Ninguna venta registrada para este evento.\n"
            
            st.text_area("Copiar para WhatsApp:", value=resumen, height=300)  # Aumentado height para más detalle
            
            # Exportaciones con detalle adicional
            col1, col2 = st.columns(2)
            if col1.button("Exportar a Excel"):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_rep.to_excel(writer, sheet_name='Cuotas', index=False)
                    df_v_evento.to_excel(writer, sheet_name='Cantina', index=False)
                st.download_button("Descargar Excel", output.getvalue(), file_name=f"reporte_completo_{f_rep_str}.xlsx")
            if col2.button("Exportar a PDF"):
                output = io.BytesIO()
                c = canvas.Canvas(output, pagesize=letter)
                c.drawString(100, 750, "Reporte Municipal Puente Alto")
                c.drawString(100, 730, f"Fecha: {fecha_es}")
                c.drawString(100, 710, f"Rival: {rival}")
                c.drawString(100, 690, f"Recaudado Cuotas: ${df_rep['pagado'].sum():,}")
                c.drawString(100, 670, f"Recaudado Cantina: ${total_cantina_evento:,}")
                c.drawString(100, 650, f"Total General: ${total_general_evento:,}")
                y = 630
                if not pendientes.empty:
                    c.drawString(100, y, "Pendientes / No Pagados (Cuotas):")
                    y -= 20
                    for _, d in pendientes.iterrows():
                        falta = d['cuota'] - d['pagado']
                        c.drawString(100, y, f"- {d['nombre']} ({d['estado']}, Falta: ${falta:,})")
                        y -= 20
                y -= 20
                if not df_v_evento.empty:
                    c.drawString(100, y, "Detalle Ventas Cantina:")
                    y -= 20
                    for _, v in grouped_ventas.iterrows():
                        jugador_nombre = session.query(Jugador).filter_by(id=v['jugador_id']).first().nombre if v['jugador_id'] else 'No Asociado'
                        producto_nombre = session.query(Producto).filter_by(id=v['producto_id']).first().nombre
                        c.drawString(100, y, f"- {jugador_nombre}: {producto_nombre} (Cant: {v['cantidad']}, Total: ${v['total']:,})")
                        y -= 20
                c.save()
                st.download_button("Descargar PDF", output.getvalue(), file_name=f"reporte_completo_{f_rep_str}.pdf")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        session.close()

def historial_jugador():
    st.subheader("Historial por Jugador")
    session = get_session()
    try:
        jugadores = session.query(Jugador).order_by(Jugador.nombre).all()  # Ordenado
        if not jugadores:
            st.info("No hay jugadores.")
            return
        nombres = [j.nombre for j in jugadores]
        selected_nombre = st.selectbox("Seleccionar Jugador:", nombres)
        if selected_nombre:
            pagos = session.query(Pago).filter_by(nombre=selected_nombre).all()
            ventas_jugador = session.query(Venta).filter_by(jugador_id=session.query(Jugador).filter_by(nombre=selected_nombre).first().id).all()
            
            if not pagos and not ventas_jugador:
                st.info("No hay registros para este jugador.")
                return
            
            # Historial de cuotas
            if pagos:
                df_hist_cuotas = pd.DataFrame([{
                    'Fecha': p.fecha, 'Rival': p.rival, 'Cuota': p.cuota, 'Pagado': p.pagado, 'Estado': p.estado
                } for p in pagos])
                st.subheader("Historial de Cuotas")
                st.dataframe(df_hist_cuotas.sort_values("Fecha", ascending=False), use_container_width=True)  # Ordenado por fecha descendente
            
            # Historial de ventas en cantina
            if ventas_jugador:
                df_hist_ventas = pd.DataFrame([{
                    'Fecha': v.fecha.isoformat(),
                    'Producto': session.query(Producto).filter_by(id=v.producto_id).first().nombre,
                    'Cantidad': v.cantidad,
                    'Total': v.total
                } for v in ventas_jugador])
                st.subheader("Historial de Compras en Cantina")
                st.dataframe(df_hist_ventas.sort_values("Fecha", ascending=False), use_container_width=True)
            
            total_pagado_cuotas = sum(p.pagado for p in pagos) if pagos else 0
            total_deuda_cuotas = sum((p.cuota - p.pagado) for p in pagos) if pagos else 0
            total_compras_cantina = sum(v.total for v in ventas_jugador) if ventas_jugador else 0
            
            st.metric("Total Pagado (Cuotas)", f"${total_pagado_cuotas:,}")
            st.metric("Total Deuda (Cuotas)", f"${total_deuda_cuotas:,}", delta_color="inverse")
            st.metric("Total Compras Cantina", f"${total_compras_cantina:,}")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        session.close()