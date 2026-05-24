import streamlit as st
from textblob import TextBlob
import sqlite3

# Configuración inicial
st.title("CRM Kreactiva 🚀")

# Conexión a base de datos
conn = sqlite3.connect('crm_kreactiva.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clientes 
             (id INTEGER PRIMARY KEY, nombre TEXT, notas TEXT, sentimiento TEXT)''')
conn.commit()

# Formulario
with st.form("registro"):
    nombre = st.text_input("Nombre")
    notas = st.text_area("Notas sobre el cliente")
    submit = st.form_submit_button("Registrar")

    if submit:
        # Lógica de sentimiento mejorada para español
        notas_lower = notas.lower()
        if any(palabra in notas_lower for palabra in ["feliz", "bueno", "excelente", "interesado", "genial"]):
            sentimiento = "Positivo 😊"
        elif any(palabra in notas_lower for palabra in ["mal", "triste", "problema", "queja", "caro"]):
            sentimiento = "Negativo 😡"
        else:
            # Fallback a TextBlob
            pol = TextBlob(notas).sentiment.polarity
            sentimiento = "Positivo 😊" if pol > 0 else "Negativo 😡" if pol < 0 else "Neutral 😐"
        
        # Guardar en BD
        c.execute("INSERT INTO clientes (nombre, notas, sentimiento) VALUES (?,?,?)",
                  (nombre, notas, sentimiento))
        conn.commit()
        st.write(f"Sentimiento detectado: {sentimiento}")
        st.success("Guardado en base de datos")

# Mostrar Pipeline
st.subheader("Pipeline de Ventas")
datos = c.execute("SELECT * FROM clientes").fetchall()
st.table(datos)
