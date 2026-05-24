import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
import sqlite3
import pandas as pd
from textblob import TextBlob

# 1. Configuración de Usuarios
passwords = ['123', 'admin123']
hashed_passwords = Hasher(passwords).generate()

credentials = {
    'usernames': {
        'asesor1': {'name': 'Vendedor 1', 'password': hashed_passwords[0], 'role': 'asesor'},
        'admin': {'name': 'Diego García', 'password': hashed_passwords[1], 'role': 'admin'}
    }
}

authenticator = stauth.Authenticate(credentials, 'crm_kreactiva', 'secret', cookie_expiry_days=30)

# 2. Login
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Si el login es exitoso, mostramos el CRM
    st.sidebar.write(f'Bienvenido {name}')
    authenticator.logout('Cerrar sesión', 'sidebar')
    
    role = credentials['usernames'][username]['role']
    
    st.title("CRM Kreactiva - HubSpot Pro 🚀")
    
    # Conexión DB
    conn = sqlite3.connect('crm_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clientes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, notas TEXT, 
                  sentimiento TEXT, probabilidad REAL, etapa TEXT, asesor TEXT)''')
    conn.commit()

    # Formulario
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
                      (nombre, notas, sentimiento, etapas_val[etapa], etapa, name))
            conn.commit()
            st.success("Guardado")

    # Pipeline filtrado
    st.subheader("Pipeline de Ventas")
    if role == 'admin':
        datos = pd.read_sql("SELECT * FROM clientes", conn)
    else:
        datos = pd.read_sql(f"SELECT * FROM clientes WHERE asesor = '{name}'", conn)
    
    st.table(datos)

elif authentication_status == False:
    st.error('Usuario o contraseña incorrectos')
elif authentication_status == None:
    st.warning('Por favor, introduce tus datos')
  
