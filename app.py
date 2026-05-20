import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    api_key = st.secrets["OPENAI_API_KEY"]
    
client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="English Coach",
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

    Reglas:
    - Explica de forma clara y sencilla.
    - Si el estudiante comete errores, corrígelos con amabilidad.
    - Da ejemplos cortos.
    - Si responde en español, puedes explicar en español.
    - Si practica conversación, responde en inglés sencillo.
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

    st.session_state.mensajes.append({
        "rol": "assistant",
        "contenido": texto_respuesta
    })