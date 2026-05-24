import streamlit as st
from textblob import TextBlob
import sqlite3

st.title("CRM Kreactiva 🚀")

# Formulario
with st.form("registro"):
    nombre = st.text_input("Nombre")
    notas = st.text_area("Notas sobre el cliente")
    submit = st.form_submit_button("Registrar")

    if submit:
        # Analisis NLP
        analisis = TextBlob(notas)
        pol = analisis.sentiment.polarity
        sentimiento = "Positivo" if pol > 0 else "Negativo" if pol < 0 else "Neutral"
        
        st.write(f"Sentimiento detectado: {sentimiento}")
        st.success("Guardado en base de datos")

st.subheader("Pipeline")
