import streamlit as st
from collections import Counter
import pandas as pd
import re

# === CONFIGURACIÓN DE REGLAS POR COLEGIO ===
rules = {
    "Nurmengard": {
        "1st": 500,
        "2nd": 400,
        "3rd": 300,
        "others": 100
    },
    "Hogwarts": {
        "1st": 100,
        "2nd": 50,
        "3rd": 25,
        "others": 10
    }
}

# === FUNCIÓN PARA PROCESAR RONDAS Y RETORNAR DETALLE ===
def procesar_rondas(texto, reglas):
    texto = texto.strip()
    rondas_raw = re.split(r"\n*\d+\.\s*", texto)
    rondas = [r.strip() for r in rondas_raw if r.strip()]

    puntos_totales = Counter()
    desglose = []

    for idx, ronda in enumerate(rondas, start=1):
        lineas = ronda.split('\n')
        lineas = [l.strip() for l in lineas if l.strip()]
        if len(lineas) < 2:
            continue

        equipos_linea = lineas[0]
        secuencia = ''.join(lineas[1:])
        equipos = equipos_linea.strip()
        secuencia = re.sub(r"\s+", "", secuencia.strip())

        conteo = Counter([c for c in secuencia if c in equipos])
        if not conteo:
            continue

        orden_aparicion = []
        for c in secuencia:
            if c in equipos and c not in orden_aparicion:
                orden_aparicion.append(c)

        ordenado = sorted(
            conteo.items(),
            key=lambda x: (-x[1], orden_aparicion.index(x[0]))
        )

        asignados = {}
        for i, (equipo, _) in enumerate(ordenado):
            if i == 0:
                asignados[equipo] = reglas["1st"]
            elif i == 1:
                asignados[equipo] = reglas["2nd"]
            elif i == 2:
                asignados[equipo] = reglas["3rd"]
            else:
                asignados[equipo] = reglas["others"]

        puntos_totales.update(asignados)

        # Agrega al desglose
        for equipo, puntos in asignados.items():
            desglose.append({
                "Ronda": idx,
                "Equipo": equipo,
                "Puntos": puntos
            })

    return puntos_totales, desglose

# === INTERFAZ STREAMLIT ===
st.title("Contador de Puntos por Colegio")

colegio = st.selectbox("Selecciona el colegio", list(rules.keys()))
nombre_dinamica = st.text_input("Nombre de la dinámica", placeholder="Ej. Adivina el país")
texto = st.text_area("Pega aquí las rondas con formato:", height=300, placeholder="1.\n🧡🩶💚\n🧡🧡🩶...")

mostrar_tabla = st.checkbox("Mostrar desglose por ronda")

if st.button("Calcular puntaje"):
    if not texto.strip() or not nombre_dinamica.strip():
        st.warning("Por favor, completa todos los campos.")
    else:
        resultado, desglose = procesar_rondas(texto, rules[colegio])
        if resultado:
            st.subheader("Resultado final (listo para copiar)")
            resultado_texto = nombre_dinamica.strip() + '\n'
            for equipo, puntos in resultado.most_common():
                resultado_texto += f"{equipo} {puntos:,}\n"

            st.code(resultado_texto.strip(), language="markdown")

            if mostrar_tabla:
                st.subheader("Desglose por ronda")
                df = pd.DataFrame(desglose)
                df = df.sort_values(by=["Ronda", "Puntos"], ascending=[True, False])
                st.dataframe(df, use_container_width=True)

        else:
            st.warning("No se encontraron datos válidos para procesar.")
