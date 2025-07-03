import streamlit as st
from collections import defaultdict
import pandas as pd
import re

# Reglas por colegio
COLEGIOS = {
    "Nurmengard": {
        "1st": 500,
        "2nd": 400,
        "3rd": 300,
        "others": 100
    }
}

st.title("Contador de Puntos")

colegio = st.selectbox("Selecciona el colegio:", list(COLEGIOS.keys()))
nombre_dinamica = st.text_input("Nombre de la dinámica:")
texto = st.text_area("Pega las rondas aquí (cada ronda debe tener 2 líneas).")

mostrar_desglose = st.checkbox("Mostrar desglose por ronda", value=True)

def procesar_rondas_detallado(texto, reglas):
    rondas_raw = re.split(r"\n*\d+\.\s*", texto.strip())
    rondas_raw = [r.strip() for r in rondas_raw if r.strip()]

    puntos_totales = defaultdict(int)
    resumen_lugares = defaultdict(lambda: defaultdict(int))
    desglose = {}

    for idx, ronda in enumerate(rondas_raw, start=1):
        lineas = ronda.split('\n')
        lineas = [l.strip() for l in lineas if l.strip()]
        if len(lineas) != 2:
            continue

        linea_corta = lineas[0]
        linea_larga = lineas[1].replace(' ', '')

        podio = list(linea_corta)
        if len(podio) < 3:
            continue

        apariciones_extras = defaultdict(int)
        for c in linea_larga:
            apariciones_extras[c] += 1

        tabla_ronda = []

        for i, lugar in enumerate(["1st", "2nd", "3rd"]):
            emoji = podio[i]
            extras = apariciones_extras.get(emoji, 0)
            puntos = reglas[lugar] + extras * reglas["others"]
            detalle = f"(1×{reglas[lugar]}) + ({extras}×{reglas['others']})"
            puntos_totales[emoji] += puntos
            resumen_lugares[emoji][lugar] += 1
            tabla_ronda.append({
                "Ronda": idx,
                "Equipo": emoji,
                "Lugar": lugar,
                "Apariciones extra": extras,
                "Puntos": puntos,
                "Detalle del cálculo": detalle
            })

        for emoji, cantidad in apariciones_extras.items():
            if emoji not in podio:
                puntos = cantidad * reglas["others"]
                puntos_totales[emoji] += puntos
                resumen_lugares[emoji]["others"] += 1
                detalle = f"({cantidad}×{reglas['others']})"
                tabla_ronda.append({
                    "Ronda": idx,
                    "Equipo": emoji,
                    "Lugar": "others",
                    "Apariciones extra": cantidad,
                    "Puntos": puntos,
                    "Detalle del cálculo": detalle
                })

        desglose[idx] = pd.DataFrame(sorted(tabla_ronda, key=lambda x: x["Puntos"], reverse=True))

    return puntos_totales, resumen_lugares, desglose

if texto and nombre_dinamica and colegio:
    reglas = COLEGIOS[colegio]
    resultado, resumen_lugares, desglose = procesar_rondas_detallado(texto, reglas)
    
    st.markdown(f"### {nombre_dinamica}")
    resultado_ordenado = sorted(resultado.items(), key=lambda x: x[1], reverse=True)
    for equipo, puntos in resultado_ordenado:
        st.write(f"{equipo} {puntos:,}")

    if mostrar_desglose:
        st.markdown("---")
        st.markdown("### Desglose por ronda")
        for ronda, tabla in desglose.items():
            st.markdown(f"**Ronda {ronda}**")
            st.dataframe(tabla, use_container_width=True)
