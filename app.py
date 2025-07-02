import streamlit as st
from collections import Counter

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

# === FUNCIÓN PARA PROCESAR RONDAS ===
def procesar_rondas(texto, reglas):
    rondas = texto.strip().split('\n\n')
    puntos_totales = Counter()

    for ronda in rondas:
        lineas = ronda.strip().split('\n')
        if len(lineas) < 3:
            continue
        equipos_linea = lineas[1]
        secuencia = lineas[2]

        equipos = equipos_linea.strip()
        secuencia = secuencia.strip()

        conteo = Counter([c for c in secuencia if c in equipos])
        if not conteo:
            continue

        # Obtener top 3 únicos equipos por orden de aparición
        orden_aparicion = []
        for c in secuencia:
            if c in equipos and c not in orden_aparicion:
                orden_aparicion.append(c)

        ordenado = sorted(conteo.items(), key=lambda x: (-x[1], orden_aparicion.index(x[0])))

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

    return puntos_totales

# === INTERFAZ STREAMLIT ===
st.title("Contador de Puntos por Colegio")

colegio = st.selectbox("Selecciona el colegio", list(rules.keys()))
nombre_dinamica = st.text_input("Nombre de la dinámica", placeholder="Ej. Adivina el país")
texto = st.text_area("Pega aquí las rondas con formato:", height=300, placeholder="1.\n🧡🩶💚\n🧡🧡🩶...")

if st.button("Calcular puntaje"):
    if not texto.strip() or not nombre_dinamica.strip():
        st.warning("Por favor, completa todos los campos.")
    else:
        resultado = procesar_rondas(texto, rules[colegio])
        if resultado:
            st.subheader("Resultado final (listo para copiar)")
            resultado_texto = nombre_dinamica.strip() + '\n'
            for equipo, puntos in resultado.most_common():
                resultado_texto += f"{equipo} {puntos:,}\n"

            st.code(resultado_texto.strip(), language="markdown")
        else:
            st.warning("No se encontraron datos válidos para procesar.")
