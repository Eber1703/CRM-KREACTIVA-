import streamlit as st
import sqlite3
import pandas as pd
import spacy

# --- CARGA EFICIENTE DEL MODELO ---
@st.cache_resource
def cargar_modelo():
    # Carga el modelo de español
    return spacy.load("es_core_news_sm")

nlp = cargar_modelo()

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
            # --- ANÁLISIS DE SENTIMIENTO CON SPACY ---
            doc = nlp(notas.lower())
            
            # Definimos listas de palabras para dar contexto al modelo
            positivas = ["feliz", "bien", "excelente", "genial", "gracias", "interesado"]
            negativas = ["mal", "caro", "problema", "no", "pesimo", "cancelar"]
            
            # Calculamos una polaridad simple basada en las palabras detectadas
            score = 0
            for token in doc:
                if token.text in positivas:
                    score += 1
                elif token.text in negativas:
                    score -= 1
            
            if score > 0:
                sentimiento = "Positivo 😊"
            elif score < 0:
                sentimiento = "Negativo 😡"
            else:
                sentimiento = "Neutral 😐"
                
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO clientes (nombre, notas, sentimiento, probabilidad, etapa, asesor) 
                              VALUES (?, ?, ?, ?, ?, ?)''', 
                           (nombre, notas, sentimiento, score, etapa, st.session_state.user_name))
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
  
