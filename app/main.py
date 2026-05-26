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

    st.subheader("Key Performance Indicators (KPIs)")
    kpis = manager.get_general_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Accounts", 
            value=f"{kpis['total_companies']:,}",
            help="Total number of B2B client companies in the database."
        )
    with col2:
        # Calculate percentage of active accounts
        active_pct = (kpis['active_companies'] / kpis['total_companies'] * 100) if kpis['total_companies'] > 0 else 0
        st.metric(
            label="Active Accounts", 
            value=f"{kpis['active_companies']:,}",
            delta=f"{active_pct:.1f}% of total",
            delta_color="normal",
            help="Accounts with an 'Active' contract status."
        )
    with col3:
        st.metric(
            label="Active Annual Revenue", 
            value=f"${kpis['total_revenue']:.2f}M",
            help="Sum of annual revenue from active contracts."
        )
    with col4:
        st.metric(
            label="Total Contacts", 
            value=f"{kpis['total_contacts']:,}",
            help="Total number of employees (contacts) registered across all companies."
        )


    st.subheader("Análisis de Rendimiento y Riesgo")
    st.info("Los gráficos de Plotly se agregarán aquí.")

    st.subheader("Inteligencia Accionable")
    st.info("Las tablas de priorización y riesgo se agregarán aquí.")

if __name__ == "__main__":
    main()
