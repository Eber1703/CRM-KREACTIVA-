import streamlit as st
import sqlite3
import pandas as pd
from textblob import TextBlob

st.title("CRM Kreactiva - HubSpot Pro 🚀")

# CAMBIAMOS EL NOMBRE A 'crm_v2.db' para forzar una base de datos limpia
conn = sqlite3.connect('crm_v2.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS clientes 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, notas TEXT, 
              sentimiento TEXT, probabilidad REAL, etapa TEXT, asesor TEXT)''')
conn.commit()

# ... (El resto del código se mantiene igual)
st.sidebar.header("Dashboard del Vendedor")
vendedor_nombre = st.sidebar.text_input("Nombre del Vendedor")

with st.form("registro"):
    nombre = st.text_input("Nombre del Cliente")
    notas = st.text_area("Notas")
    etapa = st.selectbox("Etapa del proceso", 
                         ["1. Primer Contacto", "2. Segunda Llamada", "3. Propuesta Enviada", "4. Cierre"])
    submit = st.form_submit_button("Guardar Registro")

    if submit:
        pol = TextBlob(notas).sentiment.polarity
        sentimiento = "Positivo 😊" if pol > 0 else "Negativo 😡" if pol < 0 else "Neutral 😐"
        etapas_val = {"1. Primer Contacto": 0.2, "2. Segunda Llamada": 0.4, "3. Propuesta Enviada": 0.7, "4. Cierre": 0.9}
        probabilidad = etapas_val[etapa]
        
        c.execute("INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa, asesor) VALUES (?,?,?,?,?,?)",
                  (nombre, notas, sentimiento, probabilidad, etapa, vendedor_nombre))
        conn.commit()
        st.success("Guardado correctamente")

st.subheader("Pipeline de Ventas")
datos = pd.read_sql("SELECT * FROM clientes", conn)
if not datos.empty:
    st.bar_chart(datos['etapa'].value_counts())
    st.table(datos)
  
