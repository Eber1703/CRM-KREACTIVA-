import streamlit as st
from textblob import TextBlob
import sqlite3

st.title("CRM Kreactiva - IA 🚀")

# Conexión a BD (añadimos columna 'probabilidad')
conn = sqlite3.connect('crm_kreactiva.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clientes 
             (id INTEGER PRIMARY KEY, nombre TEXT, notas TEXT, sentimiento TEXT, probabilidad REAL)''')
conn.commit()

with st.form("registro"):
    nombre = st.text_input("Nombre")
    notas = st.text_area("Notas sobre el cliente")
    num_contactos = st.number_input("Número de contactos realizados", min_value=0, step=1)
    submit = st.form_submit_button("Registrar Cliente")

    if submit:
        # NLP: Sentimiento
        notas_lower = notas.lower()
        if any(p in notas_lower for p in ["feliz", "bueno", "excelente", "interesado"]):
            sentimiento = "Positivo 😊"
            base_prob = 0.5
        elif any(p in notas_lower for p in ["mal", "triste", "problema", "queja"]):
            sentimiento = "Negativo 😡"
            base_prob = 0.1
        else:
            pol = TextBlob(notas).sentiment.polarity
            sentimiento = "Positivo 😊" if pol > 0 else "Negativo 😡" if pol < 0 else "Neutral 😐"
            base_prob = 0.3

        # ML simplificado (Probabilidad)
        # Sumamos 0.1 por cada contacto, máximo hasta 0.95
        probabilidad = min(base_prob + (num_contactos * 0.1), 0.95)
        
        c.execute("INSERT INTO clientes (nombre, notas, sentimiento, probabilidad) VALUES (?,?,?,?)",
                  (nombre, notas, sentimiento, probabilidad))
        conn.commit()
        st.write(f"Sentimiento: {sentimiento} | Probabilidad de cierre: {probabilidad*100:.0f}%")
        st.success("Guardado en base de datos")

st.subheader("Pipeline de Ventas")
datos = c.execute("SELECT * FROM clientes").fetchall()
st.table(datos)
