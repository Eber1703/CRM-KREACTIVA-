import streamlit as st
import sqlite3
import pandas as pd
import spacy

# --- CARGA EFICIENTE DEL MODELO ---
@st.cache_resource
def cargar_modelo():
    return spacy.load("es_core_news_sm")

nlp = cargar_modelo()

# --- CONFIGURACIÓN DE BASE DE DATOS ---
def get_connection():
    return sqlite3.connect('crm_v2.db')

def obtener_datos(role, user_name):
    """Función independiente para recuperar datos de forma segura."""
    conn = get_connection()
    if role == 'admin':
        query = "SELECT * FROM clientes ORDER BY id DESC"
    else:
        query = f"SELECT * FROM clientes WHERE asesor = '{user_name}' ORDER BY id DESC"
    
    datos = pd.read_sql(query, conn)
    conn.close()
    return datos

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
    
    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("Nombre del Cliente")
        notas = st.text_area("Notas")
        etapa = st.selectbox("Etapa", ["1. Primer Contacto", "2. Segunda Llamada"])
        submit = st.form_submit_button("Guardar Registro")
        
        if submit:
            # --- ANÁLISIS ---
            doc = nlp(notas.lower())
            positivas = ["feliz", "bien", "excelente", "genial", "gracias", "interesado"]
            negativas = ["mal", "caro", "problema", "no", "pesimo", "cancelar"]
            
            score = sum(1 for token in doc if token.text in positivas) - \
                    sum(1 for token in doc if token.text in negativas)
            
            sentimiento = "Positivo 😊" if score > 0 else "Negativo 😡" if score < 0 else "Neutral 😐"
                
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa, asesor) 
                              VALUES (?, ?, ?, ?, ?, ?)''', 
                           (nombre, notas, sentimiento, score, etapa, st.session_state.user_name))
            conn.commit()
            conn.close()
            st.success("Guardado correctamente")
            # Forzamos un rerun limpio tras el guardado
            st.rerun()

    # --- PIPELINE ---
    st.subheader("Pipeline de Ventas")
    # Utilizamos la función aislada para obtener los datos
    df_clientes = obtener_datos(st.session_state.role, st.session_state.user_name)
    st.table(df_clientes)
  
