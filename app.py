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
    }
}

# === FUNCIÓN PARA PROCESAR RONDAS ===
def procesar_rondas(texto, reglas):
    texto = texto.strip()
    rondas_raw = re.split(r"\n*\d+\.\s*", texto)
    rondas = [r.strip() for r in rondas_raw if r.strip()]

    puntos_totales = Counter()
    desglose = {}

    for idx, ronda in enumerate(rondas, start=1):
        lineas = ronda.split('\n')
        lineas = [l.strip() for l in lineas if l.strip()]
        if len(lineas) < 2:
            continue

        equipos_linea = lineas[0]
        secuencia = ''.join(lineas[1:])
        equipos = equipos_linea.strip()
        secuencia = re.sub(r"\s+", "", secuencia.strip())

        orden_aparicion = []
        for c in secuencia:
            if c not in orden_aparicion:
                orden_aparicion.append(c)

        podio = orden_aparicion[:3]
        conteo = Counter([c for c in secuencia])

        datos_ronda = []
        total_ronda = 0

        for equipo in conteo:
            apariciones = conteo[equipo]

            if equipo == podio[0]:
                puntos = reglas["1st"] + (apariciones - 1) * reglas["others"]
            elif len(podio) > 1 and equipo == podio[1]:
                puntos = reglas["2nd"] + (apariciones - 1) * reglas["others"]
            elif len(podio) > 2 and equipo == podio[2]:
                puntos = reglas["3rd"] + (apariciones - 1) * reglas["others"]
            else:
                puntos = apariciones * reglas["others"]

            puntos_totales[equipo] += puntos
            total_ronda += puntos

            datos_ronda.append({
                "Equipo": equipo,
                "Apariciones": apariciones,
                "Puntos": puntos
            })

        desglose[idx] = {
            "total": total_ronda,
            "datos": datos_ronda
        }

    return puntos_totales, desglose

# === INTERFAZ DE USUARIO ===
st.title("Contador de Puntos por Colegio")

colegio = st.selectbox("Selecciona el colegio", list(rules.keys()))
nombre_dinamica = st.text_input("Nombre de la dinámica", placeholder="Ej. Adivina el país")
texto = st.text_area("Pega aquí las rondas con formato:", height=300, placeholder="1.\n🧡🩶💚\n🧡🧡🩶...")

mostrar_tabla = st.checkbox("Mostrar desglose por ronda agrupado")

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
                for ronda, info in desglose.items():
                    st.markdown(f"### Ronda {ronda} — Total: {info['total']:,} puntos")
                    df = pd.DataFrame(info["datos"])
                    df = df.sort_values(by="Puntos", ascending=False)
                    st.table(df)
        else:
            st.warning("No se encontraron datos válidos para procesar.")
