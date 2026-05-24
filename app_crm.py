import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="CRM Kreactiva", page_icon="🚀")

st.title("CRM Kreactiva 🚀")

# Función para listar archivos JSON
def obtener_archivos():
    return [f for f in os.listdir('.') if f.endswith('.json')]

st.subheader("Estado del Pipeline")

archivos = obtener_archivos()

if not archivos:
    st.info("No hay clientes registrados todavía.")
else:
    for archivo in archivos:
        with open(archivo, "r") as f:
            datos = json.load(f)
            fecha_act = datetime.strptime(datos["fecha_act"], "%Y-%m-%d")
            dias_pasados = (datetime.now() - fecha_act).days
            
            if dias_pasados > 3:
                st.error(f"⚠️ {datos['nombre']} - {dias_pasados} días sin movimiento.")
            else:
                st.success(f"✅ {datos['nombre']} está al día.")

if st.button("Actualizar Vista"):
    st.rerun()
  
