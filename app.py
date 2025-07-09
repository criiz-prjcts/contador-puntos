import streamlit as st
import re
from collections import defaultdict

# Reglas por colegio
REGLAS_COHORTES = {
    "Nurmengard": {
        "first": 500,
        "second": 400,
        "third": 300,
        "others": 100
    },
    "Nurmengard_Expres": {
        "first": 200,
        "second": 100,
        "third": 100,
        "others": 100
    }
}

def parse_input(texto):
    rondas_raw = re.findall(r'(\d+\.\n(?:.+\n)+)', texto)
    rondas = []
    for ronda_raw in rondas_raw:
        lineas = ronda_raw.strip().split('\n')[1:]  # omitimos el número de ronda
        if len(lineas) == 1:
            referencia = lineas[0].strip()
            conteo = referencia
        elif len(lineas) == 2:
            referencia, conteo = lineas
            referencia = referencia.strip()
            conteo = conteo.strip()
        else:
            continue  # formato inválido
        rondas.append((referencia, conteo))
    return rondas

def procesar_rondas(rondas, reglas, desglose_por_ronda):
    puntajes = defaultdict(int)
    detalle = []

    for idx, (referencia, conteo) in enumerate(rondas, 1):
        apariciones = list(conteo)
        equipos_ronda = defaultdict(int)
        for emoji in apariciones:
            equipos_ronda[emoji] += 1

        lugares = []
        for emoji in referencia:
            if emoji not in lugares:
                lugares.append(emoji)
                if len(lugares) == 3:
                    break

        ronda_detalle = f"Ronda {idx}"
        for equipo, cantidad in equipos_ronda.items():
            if equipo == lugares[0]:
                puntos = reglas["first"] + (cantidad - 1) * reglas["others"]
                formula = f"(1×{reglas['first']}) + ({cantidad - 1}×{reglas['others']})"
            elif equipo == lugares[1]:
                puntos = reglas["second"] + (cantidad - 1) * reglas["others"]
                formula = f"(1×{reglas['second']}) + ({cantidad - 1}×{reglas['others']})"
            elif equipo == lugares[2]:
                puntos = reglas["third"] + (cantidad - 1) * reglas["others"]
                formula = f"(1×{reglas['third']}) + ({cantidad - 1}×{reglas['others']})"
            else:
                puntos = cantidad * reglas["others"]
                formula = f"{cantidad}×{reglas['others']}"

            puntajes[equipo] += puntos
            if desglose_por_ronda:
                ronda_detalle += f"\n{equipo}: {cantidad} apariciones → {puntos} puntos ({formula})"

        if desglose_por_ronda:
            detalle.append(ronda_detalle)

    return puntajes, detalle

st.title("Contador de puntos por colegio 🏆")

colegio = st.selectbox("Selecciona el colegio:", list(REGLAS_COHORTES.keys()))
reglas = REGLAS_COHORTES[colegio]

dinamica = st.text_input("Nombre de la dinámica:")
texto_entrada = st.text_area("Pega aquí las rondas:")
desglose = st.checkbox("Mostrar desglose por ronda")

if st.button("Calcular puntuaciones"):
    if not texto_entrada.strip() or not dinamica.strip():
        st.warning("Por favor ingresa un nombre de dinámica y texto válido.")
    else:
        try:
            rondas = parse_input(texto_entrada)
            puntajes, detalles = procesar_rondas(rondas, reglas, desglose)

            resultado_texto = f"{dinamica}\n"
            for equipo, puntos in sorted(puntajes.items(), key=lambda x: -x[1]):
                resultado_texto += f"{equipo} {puntos:,}\n"

            st.text_area("Resultado total", value=resultado_texto.strip(), height=150, help="Puedes copiar este bloque.")

            if desglose:
                for bloque in detalles:
                    st.markdown(f"""```\n{bloque}\n```""")

        except Exception as e:
            st.error(f"Error al procesar las rondas: {e}")
