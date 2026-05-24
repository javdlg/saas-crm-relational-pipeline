import streamlit as st
import os
import sys

# Agregar el directorio raíz al path para poder importar desde src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.business import CRMManager

# Configuración básica de la página
st.set_page_config(
    page_title="B2B CRM Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_manager():
    """
    Instancia el CRMManager una sola vez usando el caché de Streamlit
    para evitar crear múltiples conexiones a la base de datos con cada interacción.
    """
    return CRMManager()

def main():
    """Función principal para renderizar el Dashboard de Streamlit."""
    # Inicializar la conexión al backend
    manager = get_manager()

    # Título principal de la aplicación
    st.title("📊 B2B Custom CRM Intelligence")
    st.markdown("---")
    
    # Marcadores de posición para las futuras secciones
    st.sidebar.header("⚙️ Panel de Filtros")
    st.sidebar.info("Los filtros interactivos se agregarán aquí.")

    st.subheader("Indicadores Clave de Rendimiento (KPIs)")
    st.info("Las tarjetas de KPIs se agregarán aquí.")

    st.subheader("Análisis de Rendimiento y Riesgo")
    st.info("Los gráficos de Plotly se agregarán aquí.")

    st.subheader("Inteligencia Accionable")
    st.info("Las tablas de priorización y riesgo se agregarán aquí.")

if __name__ == "__main__":
    main()
