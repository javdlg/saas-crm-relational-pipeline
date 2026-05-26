import streamlit as st
import plotly.express as px
import os
import sys

# Agregar el directorio raíz y src al path para resolver importaciones internas de la carpeta src
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'src'))
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


    st.subheader("Performance & Risk Analysis")
    
    rep_df = manager.calculate_rep_performance()
    status_df = manager.get_contract_status_distribution()
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # 1. Horizontal Bar Chart of Active Revenue by Sales Rep
        fig_rep = px.bar(
            rep_df,
            x='active_revenue_m',
            y='sales_rep',
            orientation='h',
            title="Active Annual Revenue by Sales Representative ($M)",
            labels={'active_revenue_m': 'Active Revenue ($M)', 'sales_rep': 'Sales Rep'},
            color='active_revenue_m',
            color_continuous_scale='Blues',
            text_auto='.2f'
        )
        fig_rep.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        st.plotly_chart(fig_rep, use_container_width=True)
        
    with chart_col2:
        # 2. Donut Chart of Contract Status (Risk Distribution)
        fig_risk = px.pie(
            status_df,
            names='contract_status',
            values='count',
            hole=0.4,
            title="Accounts by Contract Status (Risk Profile)",
            color='contract_status',
            color_discrete_map={
                'Active': '#2b5c8f',    # Premium Navy/Blue
                'Pending': '#e6a100',   # Premium Amber
                'Expired': '#c93b2b'    # Premium Crimson/Red
            }
        )
        fig_risk.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_risk, use_container_width=True)


    st.subheader("Actionable Intelligence")
    
    # Fetch data
    contact_df = manager.calculate_contact_scoring()
    risk_df = manager.identify_at_risk_accounts()
    
    # Create tabbed layout
    tab1, tab2 = st.tabs([
        "🎯 High-Value Contacts (Priority Call List)", 
        "⚠️ At-Risk Accounts (Churn Prevention)"
    ])
    
    with tab1:
        st.markdown("### Top Contacts by Influence & Campaign Engagement")
        st.caption("Focus your outreach on these high-influence decision makers with proven campaign response rates.")
        
        # Prepare for display
        display_contacts = contact_df[[
            'name', 'job_title', 'industry', 'decision_maker_flag', 'owner_rep', 'score'
        ]].copy()
        display_contacts.columns = [
            'Contact Name', 'Job Title', 'Industry', 'Decision Maker', 'Sales Rep', 'Engagement Score'
        ]
        
        # Render interactive table with custom progress bar config
        st.dataframe(
            display_contacts,
            use_container_width=True,
            column_config={
                "Engagement Score": st.column_config.ProgressColumn(
                    "Engagement Score",
                    help="Engagement Score calculated based on influence score, response rate, and decision-maker status.",
                    format="%.1f",
                    min_value=0,
                    max_value=100
                ),
                "Decision Maker": st.column_config.TextColumn(
                    "Decision Maker",
                    help="Indicates if the contact is a primary decision maker."
                )
            },
            hide_index=True
        )
        
    with tab2:
        st.markdown("### Accounts Requiring Immediate Attention")
        st.caption("These accounts have expired or pending contracts with no recent purchase activity, or purchase rarely.")
        
        # Prepare for display
        display_risk = risk_df[[
            'company_id', 'industry', 'contract_status', 'days_since_last_purchase', 'frequency_of_purchase', 'annual_revenue', 'sales_rep'
        ]].copy()
        display_risk.columns = [
            'Company ID', 'Industry', 'Contract Status', 'Days Since Last Purchase', 'Purchase Frequency', 'Annual Revenue ($M)', 'Sales Rep'
        ]
        
        # Render interactive table with beautiful formatting
        st.dataframe(
            display_risk,
            use_container_width=True,
            column_config={
                "Annual Revenue ($M)": st.column_config.NumberColumn(
                    "Annual Revenue ($M)",
                    format="$%.2fM"
                ),
                "Days Since Last Purchase": st.column_config.NumberColumn(
                    "Days Since Last Purchase",
                    format="%d days"
                )
            },
            hide_index=True
        )


if __name__ == "__main__":
    main()
