# utils.py
from datetime import date
import re

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def calcular_edad(f_nac):
    try:
        hoy = date.today()
        return hoy.year - f_nac.year - ((hoy.month, hoy.day) < (f_nac.month, f_nac.day))
    except:
        return 0

def formatear_rut(rut):
    rut = re.sub(r'[.-]', '', rut).upper()
    if len(rut) < 2:
        return rut
    cuerpo, dv = rut[:-1], rut[-1]
    try:
        cuerpo = str(int(cuerpo))
    except ValueError:
        return rut
    return f"{cuerpo}-{dv}"

def validar_rut(rut):
    rut = formatear_rut(rut)
    if not re.match(r'^\d+-[0-9K]$', rut):
        return False
    cuerpo, dv = rut.split('-')
    reverse = map(int, reversed(cuerpo))
    factors = [2, 3, 4, 5, 6, 7] * (len(cuerpo) // 6 + 1)
    suma = sum(x * y for x, y in zip(reverse, factors))
    calc_dv = (-suma) % 11
    calc_dv = 'K' if calc_dv == 10 else str(calc_dv)
    return calc_dv == dv.upper()

def formato_fecha_es(d):
    return f"{d.day} de {MESES_ES[d.month]}, {d.year}"