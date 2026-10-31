import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Dos sobres, dos reglas", page_icon="🌱")

MODEL = st.secrets.get("MODEL", "gemini-2.5-flash")
MAX_TURNOS = 60
OPEN = "(Inicio de la sesión: el/la estudiante acaba de abrir la actividad. Comienza el paso 1.)"

with open("instrucciones.txt", encoding="utf-8") as f:
    SYSTEM = f.read()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("Dos sobres, dos reglas")
st.caption("Tutor de IA dialógico-argumentativo · ¿Qué es un dataset de entrenamiento?")
st.caption("Prototipo diseñado con apoyo de IA, no probado con estudiantes. Autores: Diego Jiménez Arriagada y Daniel Oyanedel.")

if "msgs" not in st.session_state:
    st.session_state.msgs = []


def responder():
    contenido = [types.Content(role="user", parts=[types.Part(text=OPEN)])]
    for m in st.session_state.msgs:
        rol = "user" if m["role"] == "user" else "model"
        contenido.append(types.Content(role=rol, parts=[types.Part(text=m["content"])]))
    try:
        r = client.models.generate_content(
            model=MODEL,
            contents=contenido,
            config=types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.7),
        )
        texto = r.text or "El tutor no generó respuesta. Vuelve a enviar tu mensaje."
        st.session_state.msgs.append({"role": "assistant", "content": texto})
    except Exception as e:
        st.error("No se pudo conectar con el tutor. Intenta de nuevo en un momento.")
        st.caption(f"Detalle técnico: {type(e).__name__}")


col1, col2 = st.columns([1, 1])
with col2:
    if st.button("Empezar de nuevo"):
        st.session_state.msgs = []
        st.rerun()

if not st.session_state.msgs:
    if st.button("Empezar la actividad", type="primary"):
        with st.spinner("El tutor está escribiendo…"):
            responder()
        st.rerun()
    st.info("Vas a conversar con un tutor que no te dará la respuesta: te pedirá afirmación, evidencia y razonamiento. Son 9 pasos y el último muestra tu aprendizaje.")

for m in st.session_state.msgs:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

if st.session_state.msgs:
    if len(st.session_state.msgs) >= MAX_TURNOS:
        st.warning("Se alcanzó el largo máximo de la conversación. Usa «Empezar de nuevo».")
    else:
        texto = st.chat_input("Escribe tu respuesta…")
        if texto:
            st.session_state.msgs.append({"role": "user", "content": texto})
            with st.chat_message("user"):
                st.markdown(texto)
            with st.chat_message("assistant"):
                with st.spinner("El tutor está escribiendo…"):
                    responder()
            st.rerun()
