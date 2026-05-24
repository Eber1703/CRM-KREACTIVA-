import streamlit as st
import sqlite3
import pandas as pd
from textblob import TextBlob

st.title("CRM Kreactiva - HubSpot Pro 🚀")

# 1. Configuración de Base de Datos
conn = sqlite3.connect('crm_kreactiva.db')
c = conn.cursor()
# Creamos la tabla con las etapas solicitadas
c.execute('''CREATE TABLE IF NOT EXISTS clientes 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, notas TEXT, 
              sentimiento TEXT, probabilidad REAL, etapa TEXT, asesor TEXT)''')
conn.commit()

# 2. Módulo de Metas (Simulado)
st.sidebar.header("Dashboard del Vendedor")
vendedor_nombre = st.sidebar.text_input("Nombre del Vendedor")
meta_mensual = 10  # Meta fija de ejemplo
ventas_actuales = 4 # Esto vendría de la DB en el futuro

if vendedor_nombre:
    porcentaje = (ventas_actuales / meta_mensual) * 100
    st.sidebar.write(f"Ventas: {ventas_actuales}/{meta_mensual}")
    st.sidebar.progress(porcentaje / 100)
    st.sidebar.write(f"Comisión estimada: ${ventas_actuales * 500}")

# 3. Registro y Actualización
with st.form("registro"):
    nombre = st.text_input("Nombre del Cliente")
    notas = st.text_area("Notas")
    etapa = st.selectbox("Etapa del proceso", 
                         ["1. Primer Contacto", "2. Segunda Llamada", "3. Propuesta Enviada", "4. Cierre"])
    submit = st.form_submit_button("Guardar Registro")

    if submit:
        # NLP básico
        pol = TextBlob(notas).sentiment.polarity
        sentimiento = "Positivo 😊" if pol > 0 else "Negativo 😡" if pol < 0 else "Neutral 😐"
        
        # Lógica de probabilidad basada en etapa
        etapas_val = {"1. Primer Contacto": 0.2, "2. Segunda Llamada": 0.4, "3. Propuesta Enviada": 0.7, "4. Cierre": 0.9}
        probabilidad = etapas_val[etapa]
        
        c.execute("INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa, asesor) VALUES (?,?,?,?,?,?)",
                  (nombre, notas, sentimiento, probabilidad, etapa, vendedor_nombre))
        conn.commit()
        st.success("Guardado correctamente")

# 4. Pipeline y Gráficas
st.subheader("Pipeline de Ventas")
datos = pd.read_sql("SELECT * FROM clientes", conn)

if not datos.empty:
    # Gráfica para el director
    st.bar_chart(datos['etapa'].value_counts())
    # Tabla de datos
    st.table(datos)
  
