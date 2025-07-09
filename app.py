import streamlit as st
import re
from collections import defaultdict, Counter

# Reglas de puntuación por colegio
REGLAS_COLEGIOS = {
    "Nurmengard": {"first": 500, "second": 400, "third": 300, "others": 100},
    "Nurmengard_Expres": {"first": 200, "second": 100, "third": 100, "others": 100},
}

def procesar_rondas(entrada, reglas):
    rondas = entrada.strip().split("\n\n")
    puntajes_totales = defaultdict(int)
    desglose = {}

    for ronda in rondas:
        lineas = [l.strip() for l in ronda.strip().split("\n") if l.strip()]
        if not lineas:
            continue

        nombre_ronda = lineas[0].strip(".") if lineas[0].endswith(".") else "Ronda"
        apariciones = []

        if len(lineas) == 3:
            lugares_linea = lineas[1]
            apariciones_linea = lineas[2]
            lugares = []
            for emoji in lugares_linea:
                if emoji not in lugares:
                    lugares.append(emoji)
            apariciones = list(apariciones_linea)
        else:
            texto = ''.join(lineas[1:])
            lugares = []
            for emoji in texto:
                if emoji not in lugares:
                    lugares.append(emoji)
                    if len(lugares) == 3:
                        break
            apariciones = list(texto)

        conteo = Counter(apariciones)
        desglose[nombre_ronda] = {}

        for idx, lugar in enumerate(["first", "second", "third"]):
            if idx < len(lugares):
                equipo = lugares[idx]
                puntos_lugar = reglas[lugar]
                cantidad = conteo.get(equipo, 0)
                puntaje = puntos_lugar + (cantidad - 1) * reglas["others"] if cantidad > 0 else 0
                puntajes_totales[equipo] += puntaje
                desglose[nombre_ronda][equipo] = f"{cantidad} apariciones → {puntaje} puntos (1×{puntos_lugar}) + ({cantidad - 1}×{reglas['others']})"
                conteo.pop(equipo, None)

        for equipo, cantidad in conteo.items():
            puntos = cantidad * reglas["others"]
            puntajes_totales[equipo] += puntos
            desglose[nombre_ronda][equipo] = f"{cantidad} apariciones → {puntos} puntos ({cantidad}×{reglas['others']})"

    return puntajes_totales, desglose

st.title("Contador de Puntos por Colegio")

colegio = st.selectbox("Selecciona el colegio:", list(REGLAS_COLEGIOS.keys()))
nombre_dinamica = st.text_input("Nombre de la dinámica:", "Mi dinámica")
entrada = st.text_area("Pega aquí la entrada:", height=300)
desglosar = st.checkbox("Mostrar desglose por ronda")

if st.button("Calcular Puntajes"):
    reglas = REGLAS_COLEGIOS[colegio]
    totales, desglose = procesar_rondas(entrada, reglas)

    resultado_texto = f"{nombre_dinamica}\n"
    for equipo, puntos in sorted(totales.items(), key=lambda x: x[1], reverse=True):
        resultado_texto += f"{equipo} {puntos:,}\n"

    st.text_area("Resultado final", resultado_texto.strip(), height=150)

    if desglosar:
        st.markdown("---")
        st.subheader("Desglose por ronda")
        for ronda, datos in desglose.items():
            st.markdown(f"**{ronda}**")
            for equipo, detalle in datos.items():
                st.markdown(f"- {equipo}: {detalle}")
