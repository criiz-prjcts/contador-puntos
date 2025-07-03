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
    "Nurmengard_Expres": {
        "1st": 200,
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
        if len(lineas) < 1:
            continue

        titulo = lineas[0].strip()
        contenido = lineas[1:]

        # Si solo hay una línea con emojis
        if len(contenido) == 1:
            apariciones = list(contenido[0].strip())
            if not apariciones:
                continue
            lugares = [emoji for i, emoji in enumerate(apariciones) if emoji not in apariciones[:i]][:3]
        elif len(contenido) >= 2:
            lugares = list(contenido[0].strip())
            apariciones = list(contenido[1].strip())
        else:
            continue

        conteo = Counter(apariciones)
        ronda_detalle = []
        puntos_por_equipo = defaultdict(int)

        primer_lugar = lugares[0] if lugares else None

        for equipo, cantidad in conteo.items():
            if equipo == primer_lugar:
                puntos = rules.get("1st", 0) + (cantidad - 1) * rules.get("others", 0)
                detalle = f"(1×{rules.get('1st', 0)}) + ({cantidad - 1}×{rules.get('others', 0)})"
            else:
                puntos = cantidad * rules.get("others", 0)
                detalle = f"({cantidad}×{rules.get('others', 0)})"
            puntos_por_equipo[equipo] = puntos
            resultado[equipo] += puntos
            ronda_detalle.append((equipo, cantidad, puntos, detalle))

        desglose.append((titulo, sorted(ronda_detalle, key=lambda x: x[2], reverse=True)))

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
