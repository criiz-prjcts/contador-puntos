import streamlit as st
from collections import defaultdict, Counter
import re

# Reglas de puntuación por colegio
COLEGIOS = {
    "Nurmengard": {
        "1st": 500,
        "2nd": 400,
        "3rd": 300,
        "others": 100
    },
    "Numengard_Expres": {
        "1st": 200,
        "2nd": 0,
        "3rd": 0,
        "others": 100
    }
}

st.title("Contador de Puntos por Colegio")

colegio = st.selectbox("Selecciona el colegio", list(COLEGIOS.keys()))
nombre_dinamica = st.text_input("Nombre de la dinámica")
texto = st.text_area("Pega aquí las rondas de la competencia")
mostrar_detalle = st.checkbox("Mostrar desglose por ronda")

rules = COLEGIOS[colegio]

if st.button("Calcular puntos"):
    rondas = re.split(r"\n(?=\d+\.)", texto.strip())

    resultado = defaultdict(int)
    desglose = []

    for ronda in rondas:
        lineas = ronda.strip().split("\n")
        if len(lineas) < 2:
            continue

        # Detectar si es formato de 1 o 2 líneas
        partes = lineas[1:] if len(lineas) > 2 else [lineas[0].split(".", 1)[-1].strip()]
        if len(partes) == 1:
            linea_unica = partes[0].strip()
            apariciones = list(linea_unica)
            lugares = [apariciones[0]]
        else:
            lugares = list(partes[0].strip())
            apariciones = list(partes[1].strip())

        conteo = Counter(apariciones)
        ronda_detalle = []
        puntos_por_equipo = defaultdict(int)

        for idx, lugar in enumerate(["1st", "2nd", "3rd"]):
            if idx < len(lugares):
                equipo = lugares[idx]
                puntos = rules.get(lugar, 0)
                puntos_por_equipo[equipo] += puntos
                conteo[equipo] -= 1

        for equipo, cantidad in conteo.items():
            if cantidad > 0:
                puntos = cantidad * rules["others"]
                puntos_por_equipo[equipo] += puntos

        for equipo, puntos in puntos_por_equipo.items():
            resultado[equipo] += puntos
            detalle = f"({conteo[equipo]+1 if equipo in lugares else conteo[equipo]}×{rules['others']})"
            if equipo in lugares:
                idx = lugares.index(equipo)
                lugar_key = ["1st", "2nd", "3rd"][idx]
                especial = rules.get(lugar_key, 0)
                detalle = f"(1×{especial}) + ({conteo[equipo]}×{rules['others']})"
            ronda_detalle.append((equipo, apariciones.count(equipo), puntos_por_equipo[equipo], detalle))

        desglose.append((lineas[0], sorted(ronda_detalle, key=lambda x: x[2], reverse=True)))

    # Mostrar resultado final
    st.markdown(f"## {nombre_dinamica}")
    resultado_ordenado = sorted(resultado.items(), key=lambda x: x[1], reverse=True)

    resultado_texto = f"{nombre_dinamica}\n"
    for equipo, puntos in resultado_ordenado:
        resultado_texto += f"{equipo} {puntos:,}\n"

    st.code(resultado_texto.strip(), language="markdown")

    # Mostrar detalle por ronda
    if mostrar_detalle:
        for titulo_ronda, detalles in desglose:
            st.markdown(f"### {titulo_ronda}")
            for equipo, apariciones, puntos, formula in detalles:
                st.write(f"{equipo}: {apariciones} apariciones → {puntos} puntos {formula}")
