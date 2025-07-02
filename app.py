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

# === FUNCIÓN PARA PROCESAR RONDAS ===
def procesar_rondas(texto, reglas):
    texto = texto.strip()
    rondas_raw = re.split(r"\n*\d+\.\s*", texto)
    rondas = [r.strip() for r in rondas_raw if r.strip()]

    puntos_totales = defaultdict(int)
    desglose = {}

    for idx, ronda in enumerate(rondas, start=1):
        lineas = ronda.strip().split('\n')
        lineas = [l for l in lineas if l.strip()]
        if not lineas:
            continue

        # Detectar si hay línea de referencia
        if len(lineas) >= 2:
            linea_corta = lineas[0].strip()
            secuencia = ''.join(lineas[1:]).replace(' ', '').strip()
            podio = list(linea_corta)
        else:
            # Si solo hay una línea, usar orden de aparición en secuencia
            secuencia = lineas[0].replace(' ', '').strip()
            podio = []
            for c in secuencia:
                if c not in podio:
                    podio.append(c)
            podio = podio[:3]  # solo top 3

        conteo_apariciones = defaultdict(int)
        for c in secuencia:
            conteo_apariciones[c] += 1

        total_ronda = 0
        tabla_ronda = []

        for emoji, cantidad in conteo_apariciones.items():
            if emoji == podio[0]:
                puntos = rules["1st"] + (cantidad - 1) * rules["others"]
            elif len(podio) > 1 and emoji == podio[1]:
                puntos = rules["2nd"] + (cantidad - 1) * rules["others"]
            elif len(podio) > 2 and emoji == podio[2]:
                puntos = rules["3rd"] + (cantidad - 1) * rules["others"]
            else:
                puntos = cantidad * rules["others"]

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
texto = st.text_area("Pega aquí las rondas con formato:", height=300, placeholder="1.\n🧡🩶💚\n🧡🧡🩶...\no\n1.\n🧡🩶💚🧡🧡🩶...")

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
            st.warning("No se encontraron datos válidos para procesar.")
