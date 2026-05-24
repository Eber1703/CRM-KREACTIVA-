import streamlit as st
import sqlite3
import pandas as pd
from textblob import TextBlob

# Configuración de conexión
def get_connection():
    return sqlite3.connect('crm_v2.db')

# Inicialización de estado
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_name = None

# Lógica de Login
if not st.session_state.logged_in:
    st.title("Login Kreactiva")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if username == "asesor1" and password == "asesor1":
            st.session_state.logged_in = True
            st.session_state.role = 'asesor'
            st.session_state.user_name = "Vendedor 1"
            st.rerun()
        elif username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.session_state.role = 'admin'
            st.session_state.user_name = "Admin"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    # --- APP CRM ---
    st.title("HubSpot Pro 🚀")
    
    with st.form("registro_form"):
        nombre = st.text_input("Nombre del Cliente")
        notas = st.text_area("Notas")
        etapa = st.selectbox("Etapa", ["1. Primer Contacto", "2. Segunda Llamada"])
        submit = st.form_submit_button("Guardar Registro")
        
        if submit:
            # Análisis de sentimiento
            analysis = TextBlob(notas)
            pol = analysis.sentiment.polarity
            
            # Clasificación de sentimiento
            if pol > 0.1:
                sentimiento = "Positivo 😊"
            elif pol < -0.1:
                sentimiento = "Negativo 😡"
            else:
                sentimiento = "Neutral 😐"
                
            # Guardado en base de datos incluyendo 'pol'
            conn = get_connection()
            cursor = conn.cursor()
            # Asegúrate de que tu tabla tenga la columna 'probabilidad'
            cursor.execute('''INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa, asesor) 
                              VALUES (?, ?, ?, ?, ?, ?)''', 
                           (nombre, notas, sentimiento, pol, etapa, st.session_state.user_name))
            conn.commit()
            conn.close()
            st.success("Guardado")

    # --- PIPELINE ---
    st.subheader("Pipeline de Ventas")
    conn = get_connection()
    if st.session_state.role == 'admin':
        query = "SELECT * FROM clientes ORDER BY id DESC"
    else:
        query = f"SELECT * FROM clientes WHERE asesor = '{st.session_state.user_name}' ORDER BY id DESC"
    
    datos = pd.read_sql(query, conn)
    conn.close()
    
    st.table(datos)
  
