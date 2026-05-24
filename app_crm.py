import streamlit as st
from textblob import TextBlob
import sqlite3

st.title("CRM Kreactiva - HubSpot Pro 🚀")

conn = sqlite3.connect('crm_kreactiva.db')
c = conn.cursor()

# Estructura: añadimos 'etapa'
c.execute('''CREATE TABLE IF NOT EXISTS clientes 
             (id INTEGER PRIMARY KEY, nombre TEXT, notas TEXT, sentimiento TEXT, 
              probabilidad REAL, etapa TEXT)''')
conn.commit()

with st.form("registro"):
    nombre = st.text_input("Nombre del Cliente")
    notas = st.text_area("Notas")
    etapa = st.selectbox("Etapa del proceso", 
                         ["1. Nuevo Contacto", "2. En Seguimiento", "3. Propuesta Enviada", "4. Cerrado"])
    num_contactos = st.number_input("Contactos realizados", min_value=0)
    submit = st.form_submit_button("Registrar / Actualizar")

    if submit:
        # NLP básico
        pol = TextBlob(notas).sentiment.polarity
        sentimiento = "Positivo 😊" if pol > 0 else "Negativo 😡" if pol < 0 else "Neutral 😐"
        
        # ML básico: la etapa también influye en la probabilidad ahora
        base_prob = 0.5 if "Positivo" in sentimiento else 0.2
        mult_etapa = {"1. Nuevo Contacto": 0.1, "2. En Seguimiento": 0.3, "3. Propuesta Enviada": 0.6, "4. Cerrado": 0.9}
        probabilidad = min(base_prob + (num_contactos * 0.05) + mult_etapa[etapa], 0.95)
        
        c.execute("INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa) VALUES (?,?,?,?,?)",
                  (nombre, notas, sentimiento, probabilidad, etapa))
        conn.commit()
        st.success(f"Cliente registrado en: {etapa}")

st.subheader("Pipeline de Ventas")
datos = c.execute("SELECT * FROM clientes").fetchall()
st.table(datos)
