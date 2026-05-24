import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import pandas as pd
from textblob import TextBlob

# 1. Configuración de Usuarios
config = {
    'credentials': {
        'usernames': {
            'asesor1': {'name': 'Vendedor 1', 'password': '123', 'role': 'asesor'},
            'admin': {'name': 'Diego García', 'password': 'admin123', 'role': 'admin'}
        }
    },
    'cookie': {'name': 'crm_kreactiva', 'key': 'secret', 'expiry_days': 30}
}

# 2. Inicialización del Autenticador
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# 3. Login - Usando los argumentos obligatorios para evitar errores
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.write(f'Bienvenido {name}')
    if st.sidebar.button('Cerrar sesión'):
        authenticator.logout()
        st.rerun()
    
    role = config['credentials']['usernames'][username]['role']
    st.title("CRM Kreactiva - HubSpot Pro 🚀")
    
    # 4. Conexión DB
    conn = sqlite3.connect('crm_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clientes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, notas TEXT, 
                  sentimiento TEXT, probabilidad REAL, etapa TEXT, asesor TEXT)''')
    conn.commit()

    # 5. Formulario
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

    # 6. Pipeline filtrado
    st.subheader("Pipeline de Ventas")
    if role == 'admin':
        datos = pd.read_sql("SELECT * FROM clientes", conn)
    else:
        datos = pd.read_sql(f"SELECT * FROM clientes WHERE asesor = '{name}'", conn)
    
    st.table(datos)

elif authentication_status == False:
    st.error('Usuario o contraseña incorrectos')
elif authentication_status is None:
    st.warning('Por favor, introduce tus datos')
  
