import streamlit as st
from textblob import TextBlob
import sqlite3

st.title("CRM Kreactiva - IA 🚀")

conn = sqlite3.connect('crm_kreactiva.db')
c = conn.cursor()

# Primero: borrar la tabla vieja para que se cree con la nueva estructura
# (Úsalo solo una vez para resetear el error)
c.execute('DROP TABLE IF EXISTS clientes') 
c.execute('''CREATE TABLE clientes 
             (id INTEGER PRIMARY KEY, nombre TEXT, notas TEXT, sentimiento TEXT, probabilidad REAL)''')
conn.commit()

# ... (El resto de tu código igual que antes) ...
with st.form("registro"):
    nombre = st.text_input("Nombre")
    notas = st.text_area("Notas sobre el cliente")
    num_contactos = st.number_input("Número de contactos realizados", min_value=0, step=1)
    submit = st.form_submit_button("Registrar Cliente")

    if submit:
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

        probabilidad = min(base_prob + (num_contactos * 0.1), 0.95)
        
        c.execute("INSERT INTO clientes (nombre, notas, sentimiento, probabilidad) VALUES (?,?,?,?)",
                  (nombre, notas, sentimiento, probabilidad))
        conn.commit()
        st.write(f"Sentimiento: {sentimiento} | Probabilidad de cierre: {probabilidad*100:.0f}%")
        st.success("Guardado en base de datos")

st.subheader("Pipeline de Ventas")
datos = c.execute("SELECT * FROM clientes").fetchall()
st.table(datos)
