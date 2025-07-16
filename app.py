import streamlit as st
import re
from collections import defaultdict

st.set_page_config(page_title="Contador de Puntos", layout="centered")
st.title("📊 Contador de Puntos por Colegio")

# Configuración de reglas por colegio
reglas_por_colegio = {
    "Nurmengard": {"first": 500, "second": 400, "third": 300, "others": 100},
    "Nurmengard_Expres": {"first": 200, "second": 100, "third": 100, "others": 100},
    "Ilvermorny": {"first": 300, "second": 250, "third": 200, "fourth": 150, "others": 50},
}

colegio = st.selectbox("Selecciona el colegio:", list(reglas_por_colegio.keys()))
reglas = reglas_por_colegio[colegio]

nombre_dinamica = st.text_input("Nombre de la dinámica:", "Mi dinámica")
texto = st.text_area("Pega aquí el texto con las rondas:", height=300)
mostrar_desglose = st.checkbox("Mostrar desglose por ronda")

if st.button("Calcular puntajes"):
    rondas = re.findall(r'(\d+\.\n)([\s\S]*?)(?=\n\d+\.|\Z)', texto)
    puntajes_totales = defaultdict(int)
    desglose_texto = ""

    for i, (indice, contenido) in enumerate(rondas, 1):
        lineas = [linea.strip() for linea in contenido.strip().split('\n') if linea.strip()]
        if not lineas:
            continue

        # Definir posiciones y apariciones
        if len(lineas) == 1:
            apariciones = list(lineas[0])
            lugares = [apariciones[0]]
        else:
            lugares = list(lineas[0])
            apariciones = list(lineas[0] + lineas[1])

        conteo = defaultdict(int)
        for emoji in apariciones:
            conteo[emoji] += 1

        usados = set()
        detalles = {}

        lugar_clave = ["first", "second", "third", "fourth"]

        for idx, emoji in enumerate(lugares):
            if emoji in usados:
                continue
            usados.add(emoji)
            clave = lugar_clave[idx] if idx < len(lugar_clave) else "others"
            puntos_lugar = reglas.get(clave, reglas["others"])
            total_apariciones = conteo[emoji]
            puntos_extra = (total_apariciones - 1) * reglas["others"]
            total_puntos = puntos_lugar + puntos_extra
            puntajes_totales[emoji] += total_puntos
            detalles[emoji] = f"{emoji}: {total_apariciones} apariciones → {total_puntos} puntos (1×{puntos_lugar}) + ({total_apariciones - 1}×{reglas['others']})"

        for emoji in conteo:
            if emoji not in usados:
                total_apariciones = conteo[emoji]
                total_puntos = total_apariciones * reglas["others"]
                puntajes_totales[emoji] += total_puntos
                detalles[emoji] = f"{emoji}: {total_apariciones} apariciones → {total_puntos} puntos ({total_apariciones}×{reglas['others']})"

        if mostrar_desglose:
            desglose_texto += f"\nRonda {i}\n"
            for emoji, detalle in detalles.items():
                desglose_texto += detalle + "\n"

    resultado_ordenado = sorted(puntajes_totales.items(), key=lambda x: x[1], reverse=True)

    resultado_texto = f"{nombre_dinamica}\n"
    for equipo, puntos in resultado_ordenado:
        resultado_texto += f"{equipo} {puntos:,}\n"

    st.code(resultado_texto.strip(), language=None)

    if mostrar_desglose:
        st.markdown("---")
        st.markdown("### Desglose por ronda")
        st.text(desglose_texto.strip())