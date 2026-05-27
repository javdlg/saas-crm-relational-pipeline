import streamlit as st
import plotly.express as px
import os
import sys
import pandas as pd

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

@st.cache_data
def load_base_data():
    """
    Loads raw dataframes from the database to perform high-speed in-memory filtering.
    """
    manager = get_manager()
    companies_query = """
    SELECT c.*, sr.name AS sales_rep 
    FROM companies c 
    LEFT JOIN sales_reps sr ON c.sales_rep_id = sr.id;
    """
    employees_query = """
    SELECT e.*, sr.name AS owner_rep 
    FROM employees e 
    LEFT JOIN sales_reps sr ON e.owner_rep_id = sr.id;
    """
    companies_all = pd.read_sql_query(companies_query, manager.engine)
    employees_all = pd.read_sql_query(employees_query, manager.engine)
    return companies_all, employees_all

def main():
    """Función principal para renderizar el Dashboard de Streamlit."""
    # Inicializar la conexión al backend
    manager = get_manager()
    
    # Cargar datos base
    try:
        companies_all, employees_all = load_base_data()
        contact_all = manager.calculate_contact_scoring()
        risk_all = manager.identify_at_risk_accounts()
    except Exception as e:
        st.error(f"Error loading database records: {e}")
        st.info("⚠️ Please make sure the ETL pipeline has been successfully run (python src/processor.py).")
        return

    # Título principal de la aplicación
    st.title("📊 B2B Custom CRM Intelligence")
    st.markdown("---")
    
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("⚙️ Dashboard Filters")
    st.sidebar.markdown("Use the filters below to slice and dice the B2B CRM intelligence.")
    
    # 1. Sales Rep Filter
    reps_list = ["All Sales Representatives"] + sorted(companies_all['sales_rep'].dropna().unique().tolist())
    selected_rep = st.sidebar.selectbox("Sales Representative", reps_list)
    
    # 2. Industry Filter
    industries_list = ["All Industries"] + sorted(companies_all['industry'].dropna().unique().tolist())
    selected_industry = st.sidebar.selectbox("Industry Focus", industries_list)
    
    # Apply Filters to base datasets
    companies_df = companies_all.copy()
    employees_df = employees_all.copy()
    contact_df = contact_all.copy()
    risk_df = risk_all.copy()
    
    if selected_rep != "All Sales Representatives":
        companies_df = companies_df[companies_df['sales_rep'] == selected_rep]
        employees_df = employees_df[employees_df['owner_rep'] == selected_rep]
        contact_df = contact_df[contact_df['owner_rep'] == selected_rep]
        risk_df = risk_df[risk_df['sales_rep'] == selected_rep]
        
    if selected_industry != "All Industries":
        companies_df = companies_df[companies_df['industry'] == selected_industry]
        # Filter employees to match companies of the selected industry
        valid_comp_ids = companies_df['id'].tolist()
        employees_df = employees_df[employees_df['company_id_fk'].isin(valid_comp_ids)]
        contact_df = contact_df[contact_df['industry'] == selected_industry]
        risk_df = risk_df[risk_df['industry'] == selected_industry]
        
    # --- KEY PERFORMANCE INDICATORS (KPIs) ---
    st.subheader("Key Performance Indicators (KPIs)")
    
    total_companies = len(companies_df)
    active_companies = len(companies_df[companies_df['contract_status'] == 'Active'])
    total_revenue = float(companies_df[companies_df['contract_status'] == 'Active']['annual_revenue'].sum())
    total_contacts = len(employees_df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Accounts", 
            value=f"{total_companies:,}",
            help="Total number of B2B client companies matching the selected filters."
        )
    with col2:
        # Calculate percentage of active accounts
        active_pct = (active_companies / total_companies * 100) if total_companies > 0 else 0
        st.metric(
            label="Active Accounts", 
            value=f"{active_companies:,}",
            delta=f"{active_pct:.1f}% of total",
            delta_color="normal" if active_pct > 0 else "off",
            help="Accounts with an 'Active' contract status matching the selected filters."
        )
    with col3:
        st.metric(
            label="Active Annual Revenue", 
            value=f"${total_revenue:.2f}M",
            help="Sum of annual revenue from active contracts matching the selected filters."
        )
    with col4:
        st.metric(
            label="Total Contacts", 
            value=f"{total_contacts:,}",
            help="Total number of employees (contacts) registered under the filtered accounts."
        )

    st.markdown("---")

    # --- PERFORMANCE & RISK ANALYSIS ---
    st.subheader("Performance & Risk Analysis")
    
    if companies_df.empty:
        st.warning("⚠️ No data available matching the selected filters. Please adjust your sidebar choices.")
    else:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # 1. Horizontal Bar Chart of Active Revenue by Sales Rep (with selective highlighting)
            rep_df = manager.calculate_rep_performance()
            
            # Setup dynamic color mapping to highlight the selected Sales Rep
            if selected_rep != "All Sales Representatives":
                rep_df['Highlight'] = rep_df['sales_rep'].apply(lambda x: 'Selected' if x == selected_rep else 'Other')
                color_map = {'Selected': '#e6a100', 'Other': '#a3bccc'}
            else:
                rep_df['Highlight'] = 'All'
                color_map = {'All': '#2b5c8f'}
                
            fig_rep = px.bar(
                rep_df,
                x='active_revenue_m',
                y='sales_rep',
                orientation='h',
                title="Active Revenue Ranking by Sales Representative ($M)",
                labels={'active_revenue_m': 'Active Revenue ($M)', 'sales_rep': 'Sales Rep'},
                color='Highlight',
                color_discrete_map=color_map,
                text_auto='.2f'
            )
            fig_rep.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                height=400
            )
            st.plotly_chart(fig_rep, use_container_width=True)
            
        with chart_col2:
            # 2. Donut Chart of Contract Status (Risk Distribution) on filtered dataset
            status_df = companies_df.groupby('contract_status').size().reset_index(name='count')
            
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

    st.markdown("---")

    # --- ACTIONABLE INTELLIGENCE ---
    st.subheader("Actionable Intelligence")
    
    # Create tabbed layout
    tab1, tab2 = st.tabs([
        "🎯 High-Value Contacts (Priority Call List)", 
        "⚠️ At-Risk Accounts (Churn Prevention)"
    ])
    
    with tab1:
        st.markdown("### Top Contacts by Influence & Campaign Engagement")
        st.caption("Focus your outreach on these high-influence decision makers with proven campaign response rates.")
        
        if contact_df.empty:
            st.info("ℹ️ No high-value contacts match the selected filters.")
        else:
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
        
        if risk_df.empty:
            st.info("ℹ️ No at-risk accounts match the selected filters.")
        else:
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
