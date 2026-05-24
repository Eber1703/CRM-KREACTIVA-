import streamlit as st
import sqlite3
import pandas as pd
from textblob import TextBlob

# 1. Autenticación Manual (Simple y sin errores de librería)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("Login Kreactiva")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        # Credenciales fijas
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_name = "Diego García"
            st.session_state.role = "admin"
            st.rerun()
        elif username == "asesor1" and password == "123":
            st.session_state.logged_in = True
            st.session_state.user_name = "Vendedor 1"
            st.session_state.role = "asesor"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

# 2. Si el usuario está logueado, mostrar el CRM
st.sidebar.write(f"Bienvenido {st.session_state.user_name}")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.logged_in = False
    st.rerun()

st.title("CRM Kreactiva - HubSpot Pro 🚀")

# 3. Conexión DB
conn = sqlite3.connect('crm_v2.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clientes 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, notas TEXT, 
              sentimiento TEXT, probabilidad REAL, etapa TEXT, asesor TEXT)''')
conn.commit()

# 4. Formulario
with st.form("registro"):
    nombre = st.text_input("Nombre del Cliente")
    notas = st.text_area("Notas")
    etapa = st.selectbox("Etapa", ["1. Primer Contacto", "2. Segunda Llamada", "3. Propuesta Enviada", "4. Cierre"])
    submit = st.form_submit_button("Guardar Registro")

    if submit:
        pol = TextBlob(notas).sentiment.polarity
        sentimiento = "Positivo 😊" if pol > 0 else "Negativo 😡" if pol < 0 else "Neutral 😐"
        etapas_val = {"1. Primer Contacto": 0.2, "2. Segunda Llamada": 0.4, "3. Propuesta Enviada": 0.7, "4. Cierre": 0.9}
        
        c.execute("INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa, asesor) VALUES (?,?,?,?,?,?)",
                  (nombre, notas, sentimiento, etapas_val[etapa], etapa, st.session_state.user_name))
        conn.commit()
        st.success("Guardado")

# 5. Pipeline
st.subheader("Pipeline de Ventas")
if st.session_state.role == 'admin':
    datos = pd.read_sql("SELECT * FROM clientes", conn)
else:
    datos = pd.read_sql(f"SELECT * FROM clientes WHERE asesor = '{st.session_state.user_name}'", conn)
st.table(datos)
