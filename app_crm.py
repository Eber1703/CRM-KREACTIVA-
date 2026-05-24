import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import pandas as pd
from textblob import TextBlob

# 1. Configuración de Usuarios (Sin usar Hasher complejo para evitar errores de versión)
# En producción, usa contraseñas encriptadas. Aquí usamos texto plano para verificar que el login funcione.
names = ['Vendedor 1', 'Diego García']
usernames = ['asesor1', 'admin']
passwords = ['123', 'admin123']
hashed_passwords = stauth.Hasher(passwords).generate()

credentials = {
    'usernames': {
        usernames[0]: {'name': names[0], 'password': hashed_passwords[0], 'role': 'asesor'},
        usernames[1]: {'name': names[1], 'password': hashed_passwords[1], 'role': 'admin'}
    }
}

# 2. Autenticación
authenticator = stauth.Authenticate(credentials, 'crm_kreactiva', 'secret', cookie_expiry_days=30)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.sidebar.write(f'Bienvenido {name}')
    authenticator.logout('Cerrar sesión', 'sidebar')
    
    role = credentials['usernames'][username]['role']
    st.title("CRM Kreactiva - HubSpot Pro 🚀")
    
    # Lógica de CRM (Ya validada anteriormente)
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

    # Pipeline
    st.subheader("Pipeline de Ventas")
    if role == 'admin':
        datos = pd.read_sql("SELECT * FROM clientes", conn)
    else:
        datos = pd.read_sql(f"SELECT * FROM clientes WHERE asesor = '{name}'", conn)
    st.table(datos)

elif authentication_status == False:
    st.error('Usuario o contraseña incorrectos')
  
