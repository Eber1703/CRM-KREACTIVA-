import streamlit as st
import sqlite3
import pandas as pd
from textblob import TextBlob

st.title("CRM Kreactiva - HubSpot Pro 🚀")

conn = sqlite3.connect('crm_kreactiva.db')
c = conn.cursor()

# Recrear tabla con estructura nueva
c.execute('DROP TABLE IF EXISTS clientes')
c.execute('''CREATE TABLE clientes 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, notas TEXT, 
              sentimiento TEXT, probabilidad REAL, etapa TEXT)''')
conn.commit()

# Sidebar: Búsqueda y Edición
st.sidebar.header("Gestión de Clientes")
modo = st.sidebar.radio("Modo", ["Registrar", "Editar"])

if modo == "Registrar":
    with st.form("registro"):
        nombre = st.text_input("Nombre")
        notas = st.text_area("Notas")
        etapa = st.selectbox("Etapa", ["1. Nuevo", "2. Seguimiento", "3. Propuesta", "4. Cerrado"])
        if st.form_submit_button("Guardar"):
            pol = TextBlob(notas).sentiment.polarity
            sentimiento = "Positivo 😊" if pol > 0 else "Negativo 😡" if pol < 0 else "Neutral 😐"
            c.execute("INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa) VALUES (?,?,?,?,?)",
                      (nombre, notas, sentimiento, 0.5, etapa))
            conn.commit()
            st.success("Guardado")

else: # Modo Editar
    clientes = pd.read_sql("SELECT * FROM clientes", conn)
    nombre_sel = st.sidebar.selectbox("Seleccionar Cliente", clientes['nombre'].unique())
    cliente_data = clientes[clientes['nombre'] == nombre_sel].iloc[0]
    
    nuevo_estado = st.selectbox("Cambiar Etapa", ["1. Nuevo", "2. Seguimiento", "3. Propuesta", "4. Cerrado"], 
                                index=["1. Nuevo", "2. Seguimiento", "3. Propuesta", "4. Cerrado"].index(cliente_data['etapa']))
    if st.button("Actualizar Etapa"):
        c.execute("UPDATE clientes SET etapa = ? WHERE nombre = ?", (nuevo_estado, nombre_sel))
        conn.commit()
        st.success("Actualizado")

# Gráfica
st.subheader("Pipeline Visual")
datos = pd.read_sql("SELECT * FROM clientes", conn)
if not datos.empty:
    st.bar_chart(datos['etapa'].value_counts())
    st.table(datos)
  
