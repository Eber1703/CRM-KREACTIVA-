import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# 1. Configuración de Usuarios (En una app real, esto iría en un archivo .yaml externo)
# Aquí definimos usuarios: 'asesor1' y 'admin' (tú)
hashed_passwords = stauth.Hasher(['123', 'admin123']).generate()

config = {
    'credentials': {
        'usernames': {
            'asesor1': {'name': 'Vendedor 1', 'password': hashed_passwords[0], 'role': 'asesor'},
            'admin': {'name': 'Diego García', 'password': hashed_passwords[1], 'role': 'admin'}
        }
    },
    'cookie': {'name': 'crm_kreactiva', 'key': 'secret', 'expiry_days': 30}
}

authenticator = stauth.Authenticate(config['credentials'], config['cookie']['name'], config['cookie']['key'])

# 2. Pantalla de Login
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.sidebar.write(f'Bienvenido *{name}*')
    authenticator.logout('Cerrar sesión', 'sidebar')
    
    # Aquí iría el resto de tu lógica (CRM, base de datos, etc.)
    # Podemos usar st.session_state['role'] para diferenciar vistas
    role = config['credentials']['usernames'][username]['role']
    
    st.title("CRM Kreactiva - HubSpot Pro 🚀")
    
    if role == 'admin':
        st.subheader("Panel de Director (Vista Total)")
        # Aquí cargarás la tabla completa y las gráficas globales
    else:
        st.subheader("Panel de Asesor (Tu Cartera)")
        # Aquí filtraremos la base de datos: "SELECT * FROM clientes WHERE asesor = 'asesor1'"

elif authentication_status == False:
    st.error('Usuario o contraseña incorrectos')
elif authentication_status == None:
    st.warning('Por favor, introduce tus datos')

