import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from pypdf import PdfReader

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    api_key = st.secrets["OPENAI_API_KEY"]
    
#cCONFIGURACION GENERAL
client = OpenAI(api_key=api_key)
LIBROS_DIR = "libros"
HISTORIAL_DIR = "historial"
HISTORIAL_FILE = os.path.join(HISTORIAL_DIR, "conversaciones.json")


def guardar_conversacion(usuario, respuesta, modelo, nivel, modo):
    # Crear carpeta historial si no existe
    os.makedirs(HISTORIAL_DIR, exist_ok=True)

    # Estructura de una conversación
    nueva_conversacion = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modelo": modelo,
        "nivel": nivel,
        "modo": modo,
        "usuario": usuario,
        "respuesta": respuesta
    }

    # Leer historial anterior si existe
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as archivo:
            historial = json.load(archivo)
    else:
        historial = []

    # Agregar nueva conversación
    historial.append(nueva_conversacion)

    # Guardar historial actualizado
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as archivo:
        json.dump(historial, archivo, ensure_ascii=False, indent=4)


def leer_libros():
    textos = []

    if not os.path.exists(LIBROS_DIR):
        return ""

    for nombre_archivo in os.listdir(LIBROS_DIR):
        ruta_archivo = os.path.join(LIBROS_DIR, nombre_archivo)

        if nombre_archivo.lower().endswith(".txt"):
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                textos.append(archivo.read())

        elif nombre_archivo.lower().endswith(".pdf"):
            reader = PdfReader(ruta_archivo)
            texto_pdf = ""

            for pagina in reader.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_pdf += texto_pagina + "\n"

            textos.append(texto_pdf)

    return "\n\n".join(textos)

st.set_page_config(
    page_title="INOKI English Teacher",
    page_icon="🇬🇧",
    layout="centered"
)

# CSS personalizado
st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    max-width: 850px;
}

h1 {
    text-align: center;
    color: #1f2937;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 18px;
    margin-bottom: 25px;
}

.card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.stChatMessage {
    border-radius: 14px;
    padding: 8px;
}
</style>
""", unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.title("⚙️ Configuración")

    nivel = st.selectbox(
        "Nivel de inglés",
        ["Principiante", "Intermedio", "Avanzado"]
    )

    modo = st.selectbox(
        "Modo de práctica",
        [
            "Profesor paciente",
            "Corrección gramatical",
            "Conversación diaria",
            "Preparación para examen",
            "Traducción y explicación"
        ]
    )

    st.divider()

    if st.button("🗑️ Borrar conversación"):
        st.session_state.mensajes = []
        st.rerun()

# Encabezado
st.title("🇬🇧 English Coach")

st.markdown(
    """
    <p class="subtitle">
    Practica inglés, corrige frases y mejora tu gramática con ayuda personalizada.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="card">
        <b>Modo actual:</b> {modo}<br>
        <b>Nivel:</b> {nivel}
    </div>
    """,
    unsafe_allow_html=True
)

# Historial
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "contenido_libros" not in st.session_state:
    st.session_state.contenido_libros = leer_libros()

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["contenido"])

pregunta = st.chat_input("Escribe tu pregunta o frase en inglés...")

if pregunta:
    st.session_state.mensajes.append({
        "rol": "user",
        "contenido": pregunta
    })

    with st.chat_message("user"):
        st.write(pregunta)

    prompt_sistema = f"""
    Eres un profesor de inglés para un estudiante de nivel {nivel}.
    Tu modo actual es: {modo}.

    Usa la siguiente información de referencia tomada de libros de inglés cuando sea útil:

    {st.session_state.contenido_libros[:12000]}

   Reglas:

Antes de responder, analiza cuidadosamente:
- El mensaje actual del usuario.
- El historial de la conversación actual.
- El historial persistente de conversaciones anteriores.
- El contexto proporcionado por los libros y documentos de referencia.

Comportamiento del asistente:
- Actúa como un profesor de inglés amable, paciente y pedagógico.
- Explica los temas de forma clara, sencilla y estructurada.
- Adapta las respuestas al nivel del estudiante.
- Si el usuario comete errores gramaticales o de escritura, corrígelos de manera respetuosa y explica brevemente el error.
- Proporciona ejemplos cortos, prácticos y fáciles de entender.
- Si el usuario escribe en español, puedes responder usando español e inglés para facilitar el aprendizaje.
- Si el usuario practica conversación, responde utilizando inglés sencillo y natural.
- Mantén coherencia con conversaciones anteriores cuando sea relevante.
- Prioriza el uso de la información proporcionada por los libros y documentos.
- Si la información documental no es suficiente, utiliza tu conocimiento general.
- Evita respuestas excesivamente largas o complejas.
- Mantén un tono motivador y educativo.
    """

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            respuesta = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    *[
                        {
                            "role": m["rol"],
                            "content": m["contenido"]
                        }
                        for m in st.session_state.mensajes
                    ]
                ]
            )

            texto_respuesta = respuesta.choices[0].message.content
            st.write(texto_respuesta)
            
            guardar_conversacion(
                usuario=pregunta,
                respuesta=texto_respuesta,
                modelo="OpenAI GPT-4.1-mini",
                nivel=nivel,
                modo=modo
            )

    st.session_state.mensajes.append({
        "rol": "assistant",
        "contenido": texto_respuesta
    })