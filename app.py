import streamlit as st
from collections import defaultdict
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

# === FUNCIÓN PARA PROCESAR RONDAS CON 3 LÍNEAS ===
def procesar_rondas(texto, reglas):
    texto = texto.strip()
    rondas_raw = re.split(r"\n*\d+\.\s*", texto)
    rondas_raw = [r.strip() for r in rondas_raw if r.strip()]

    puntos_totales = defaultdict(int)
    desglose = {}

    for idx, ronda in enumerate(rondas_raw, start=1):
        lineas = ronda.split('\n')
        lineas = [l.strip() for l in lineas if l.strip()]

        if len(lineas) != 2:
            continue  # solo procesar rondas con 2 líneas después del número

        linea_corta = lineas[0]
        secuencia = lineas[1].replace(' ', '')
        podio = list(linea_corta)

        if len(podio) < 3:
            continue  # requerimos exactamente 3 emojis en la línea corta

        conteo_apariciones = defaultdict(int)
        for c in secuencia:
            conteo_apariciones[c] += 1

        total_ronda = 0
        tabla_ronda = []

        for emoji, cantidad in conteo_apariciones.items():
            if emoji == podio[0]:
                puntos = reglas["1st"] + (cantidad - 1) * reglas["others"]
            elif emoji == podio[1]:
                puntos = reglas["2nd"] + (cantidad - 1) * reglas["others"]
            elif emoji == podio[2]:
                puntos = reglas["3rd"] + (cantidad - 1) * reglas["others"]
            else:
                puntos = cantidad * reglas["others"]

            puntos_totales[emoji] += puntos
            total_ronda += puntos

            tabla_ronda.append({
                "Equipo": emoji,
                "Apariciones": cantidad,
                "Puntos": puntos
            })

        desglose[idx] = {
            "total": total_ronda,
            "datos": sorted(tabla_ronda, key=lambda x: x["Puntos"], reverse=True)
        }

    return puntos_totales, desglose

# === INTERFAZ STREAMLIT ===
st.title("Contador de Puntos por Colegio")

colegio = st.selectbox("Selecciona el colegio", list(rules.keys()))
nombre_dinamica = st.text_input("Nombre de la dinámica", placeholder="Ej. Adivina el país")
texto = st.text_area("Pega aquí las rondas (3 líneas cada una)", height=300,
                     placeholder="1.\n🧡🩶💚\n🧡🧡🩶...")

mostrar_tabla = st.checkbox("Mostrar desglose por ronda agrupado")

if st.button("Calcular puntaje"):
    if not texto.strip() or not nombre_dinamica.strip():
        st.warning("Por favor, completa todos los campos.")
    else:
        resultado, desglose = procesar_rondas(texto, rules[colegio])
        if resultado:
            st.subheader("Resultado final (listo para copiar)")
            resultado_texto = nombre_dinamica.strip() + '\n'
            for equipo, puntos in sorted(resultado.items(), key=lambda x: x[1], reverse=True):
                resultado_texto += f"{equipo} {puntos:,}\n"
            st.code(resultado_texto.strip(), language="markdown")

            if mostrar_tabla:
                st.subheader("Desglose por ronda")
                for ronda, info in desglose.items():
                    st.markdown(f"### Ronda {ronda} — Total: {info['total']:,} puntos")
                    df = pd.DataFrame(info["datos"])
                    st.table(df)
        else:
            st.warning("No se encontraron rondas válidas (deben tener 3 líneas).")
