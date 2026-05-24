import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import pandas as pd
from textblob import TextBlob

# 1. Configuración de Usuarios (Sin Hasher para evitar errores de compatibilidad)
# NOTA: En producción esto debe cambiarse, pero esto hará que tu app funcione AHORA.
credentials = {
    'usernames': {
        'asesor1': {'name': 'Vendedor 1', 'password': '123', 'role': 'asesor'},
        'admin': {'name': 'Diego García', 'password': 'admin123', 'role': 'admin'}
    }
}

# 2. Autenticación (Configuración mínima)
authenticator = stauth.Authenticate(credentials, 'crm_kreactiva', 'secret', cookie_expiry_days=30)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.sidebar.write(f'Bienvenido {name}')
    authenticator.logout('Cerrar sesión', 'sidebar')
    
    # ... resto de tu lógica de CRM (Base de datos, formulario, etc.)
    # (Mantén la misma lógica de conexión y formulario que ya teníamos)
  
