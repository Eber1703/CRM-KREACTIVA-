import streamlit as st
import sqlite3
import pandas as pd
from textblob import TextBlob

st.title("CRM Kreactiva - HubSpot Pro 🚀")

# 1. Conexión y Limpieza forzada de estructura (Solo si hay errores de columnas)
conn = sqlite3.connect('crm_kreactiva.db')
c = conn.cursor()

# Si quieres borrar los datos viejos y forzar la nueva estructura, descomenta la siguiente línea:
# c.execute('DROP TABLE IF EXISTS clientes') 

c.execute('''CREATE TABLE IF NOT EXISTS clientes 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, notas TEXT, 
              sentimiento TEXT, probabilidad REAL, etapa TEXT, asesor TEXT)''')
conn.commit()

# 2. Sidebar para metas
st.sidebar.header("Dashboard del Vendedor")
vendedor_nombre = st.sidebar.text_input("Nombre del Vendedor")

# 3. Formulario
with st.form("registro"):
    nombre = st.text_input("Nombre del Cliente")
    notas = st.text_area("Notas")
    etapa = st.selectbox("Etapa del proceso", 
                         ["1. Primer Contacto", "2. Segunda Llamada", "3. Propuesta Enviada", "4. Cierre"])
    submit = st.form_submit_button("Guardar Registro")

    if submit:
        # NLP
        pol = TextBlob(notas).sentiment.polarity
        sentimiento = "Positivo 😊" if pol > 0 else "Negativo 😡" if pol < 0 else "Neutral 😐"
        
        # Probabilidad
        etapas_val = {"1. Primer Contacto": 0.2, "2. Segunda Llamada": 0.4, "3. Propuesta Enviada": 0.7, "4. Cierre": 0.9}
        probabilidad = etapas_val[etapa]
        
        # Inserción segura
        c.execute("INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa, asesor) VALUES (?,?,?,?,?,?)",
                  (nombre, notas, sentimiento, probabilidad, etapa, vendedor_nombre))
        conn.commit()
        st.success("Guardado correctamente")

# 4. Pipeline
st.subheader("Pipeline de Ventas")
datos = pd.read_sql("SELECT * FROM clientes", conn)

if not datos.empty:
    st.bar_chart(datos['etapa'].value_counts())
    st.table(datos)
  
