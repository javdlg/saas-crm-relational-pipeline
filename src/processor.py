import os
import pandas as pd
import difflib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importamos los modelos que creamos previamente
from models import Base, SalesRep, Company, Employee

# Definimos rutas relativas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = f"sqlite:///{os.path.join(DB_DIR, 'crm_custom.db')}"
COMPANIES_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'companies_noisy_734.csv')
EMPLOYEES_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'employees_noisy_5234.csv')

def setup_database():
    """Crea el directorio de la BD si no existe y genera las tablas."""
    os.makedirs(DB_DIR, exist_ok=True)
    engine = create_engine(DB_PATH)
    # Crea todas las tablas definidas en models.py
    Base.metadata.create_all(engine)
    return engine

def safe_float(val):
    """Convierte de forma segura un valor a float manejando ruido."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def safe_int(val):
    """Convierte de forma segura un valor a int manejando ruido."""
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None

CLEAN_INDUSTRIES = [
    'Aerospace', 'Buildings', 'Data Centres', 'Food & Beverage', 'Healthcare', 
    'Machine Building', 'Mining, Metals & Minerals', 'Oil & Gas', 
    'Residential', 'Utilities', 'Vehicles'
]

def clean_industry(val):
    """Limpia y normaliza de forma segura la industria mediante coincidencia difusa."""
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    matches = difflib.get_close_matches(val_str, CLEAN_INDUSTRIES, n=1, cutoff=0.4)
    if matches:
        return matches[0]
    return val_str.title()


def process_and_load():
    """Función principal ETL: Extrae, Transforma y Carga los datos."""
    print("Iniciando proceso ETL...")
    engine = setup_database()
    Session = sessionmaker(bind=engine)
    session = Session()

    # --- 1. EXTRAER (Extract) ---
    print("Leyendo archivos CSV...")
    companies_df = pd.read_csv(COMPANIES_CSV)
    employees_df = pd.read_csv(EMPLOYEES_CSV)

    # --- 2. TRANSFORMAR (Transform) ---
    print("Limpiando y transformando datos...")
    
    # Eliminar filas donde el ID principal sea nulo (datos corruptos)
    companies_df.dropna(subset=['Company_ID'], inplace=True)
    employees_df.dropna(subset=['Employee_ID'], inplace=True)

    # Normalizar valores de texto (eliminar espacios extra)
    companies_df['Company_ID'] = companies_df['Company_ID'].astype(str).str.strip()
    employees_df['Employee_ID'] = employees_df['Employee_ID'].astype(str).str.strip()
    companies_df['Sales_Rep'] = companies_df['Sales_Rep'].astype(str).str.strip()
    employees_df['Owner_Rep'] = employees_df['Owner_Rep'].astype(str).str.strip()

    # Extraer todos los representantes de ventas únicos para poblar la tabla 'sales_reps'
    reps_companies = companies_df['Sales_Rep'].dropna().unique()
    reps_employees = employees_df['Owner_Rep'].dropna().unique()
    
    # Unir ambos sets y filtrar los "nan" o vacíos
    all_reps = set(reps_companies).union(set(reps_employees))
    all_reps = {rep for rep in all_reps if rep.lower() != 'nan' and rep != ''}

    # --- 3. CARGAR (Load) ---
    print("Cargando datos en la base de datos relacional...")

    # Cargar SalesReps
    for rep_name in all_reps:
        # Verificar si ya existe
        if not session.query(SalesRep).filter_by(name=rep_name).first():
            session.add(SalesRep(name=rep_name))
    session.commit()

    # Diccionario para mapear nombre del representante a su ID en la BD
    reps_db = session.query(SalesRep).all()
    rep_id_map = {rep.name: rep.id for rep in reps_db}

    # Cargar Companies
    for _, row in companies_df.iterrows():
        comp_id = row['Company_ID']
        
        # Evitar duplicados
        if session.query(Company).filter_by(company_id=comp_id).first():
            continue
            
        rep_name = row['Sales_Rep']
        sales_rep_id = rep_id_map.get(rep_name) if pd.notna(rep_name) else None

        company = Company(
            company_id=comp_id,
            industry=clean_industry(row['Industry']),
            company_size=str(row['Company_Size']).strip() if pd.notna(row['Company_Size']) else None,
            annual_revenue=safe_float(row['Annual_Revenue (M₺)']),
            marketing_spend=safe_float(row['Marketing_Spend (K₺)']),
            campaign_type=str(row['Campaign_Type']).strip() if pd.notna(row['Campaign_Type']) else None,
            leads_generated=safe_int(row['Leads_Generated']),
            conversion_rate=safe_float(row['Conversion_Rate (%)']),
            region=str(row['Region']).strip() if pd.notna(row['Region']) else None,
            district=str(row['District']).strip() if pd.notna(row['District']) else None,
            last_product_1=str(row['Last_Product_1']).strip() if pd.notna(row['Last_Product_1']) else None,
            last_product_2=str(row['Last_Product_2']).strip() if pd.notna(row['Last_Product_2']) else None,
            frequency_of_purchase=str(row['Frequency_of_Purchase']).strip().capitalize() if pd.notna(row['Frequency_of_Purchase']) else None,
            days_since_last_purchase=safe_int(row['Days_Since_Last_Purchase']),
            contract_status=str(row['Contract_Status']).strip().capitalize() if pd.notna(row['Contract_Status']) else None,
            total_purchases_last_year=safe_int(row['Total_Purchases_Last_Year']),
            payment_behavior=str(row['Payment_Behavior']).strip() if pd.notna(row['Payment_Behavior']) else None,
            preferred_channel=str(row['Preferred_Channel']).strip() if pd.notna(row['Preferred_Channel']) else None,
            sales_rep_id=sales_rep_id
        )
        session.add(company)
    session.commit()

    # Diccionario para mapear el ID string de la compañía a su clave primaria entera en la BD
    companies_db = session.query(Company).all()
    comp_id_map = {c.company_id: c.id for c in companies_db}

    # Cargar Employees (Contacts)
    for _, row in employees_df.iterrows():
        emp_id = row['Employee_ID']
        
        # Evitar duplicados
        if session.query(Employee).filter_by(employee_id=emp_id).first():
            continue
            
        rep_name = row['Owner_Rep']
        owner_rep_id = rep_id_map.get(rep_name) if pd.notna(rep_name) else None
        
        comp_id_str = str(row['Company_ID']).strip() if pd.notna(row['Company_ID']) else None
        company_id_fk = comp_id_map.get(comp_id_str)

        employee = Employee(
            employee_id=emp_id,
            name=str(row['Name']).strip() if pd.notna(row['Name']) else None,
            department=str(row['Department']).strip() if pd.notna(row['Department']) else None,
            job_title=str(row['Job_Title']).strip() if pd.notna(row['Job_Title']) else None,
            seniority_level=str(row['Seniority_Level']).strip() if pd.notna(row['Seniority_Level']) else None,
            education_level=str(row['Education_Level']).strip() if pd.notna(row['Education_Level']) else None,
            work_location=str(row['Work_Location']).strip() if pd.notna(row['Work_Location']) else None,
            newsletter_subscription=str(row['Newsletter_Subscription']).strip() if pd.notna(row['Newsletter_Subscription']) else None,
            campaign_response_rate=safe_float(row['Campaign_Response_Rate (%)']),
            tenure_years=safe_float(row['Tenure_Years']),
            event_attendance=safe_int(row['Event_Attendance']),
            influence_score=safe_float(row['Influence_Score']),
            decision_maker_flag=str(row['Decision_Maker_Flag']).strip().capitalize() if pd.notna(row['Decision_Maker_Flag']) else None,
            preferred_contact_method=str(row['Preferred_Contact_Method']).strip() if pd.notna(row['Preferred_Contact_Method']) else None,
            language=str(row['Language']).strip() if pd.notna(row['Language']) else None,
            last_contact_date=str(row['Last_Contact_Date']).strip() if pd.notna(row['Last_Contact_Date']) else None,
            next_followup_date=str(row['Next_Followup_Date']).strip() if pd.notna(row['Next_Followup_Date']) else None,
            active_flag=str(row['Active_Flag']).strip().capitalize() if pd.notna(row['Active_Flag']) else None,
            data_source=str(row['Data_Source']).strip() if pd.notna(row['Data_Source']) else None,
            company_id_fk=company_id_fk,
            owner_rep_id=owner_rep_id
        )
        session.add(employee)
    session.commit()

    print("¡Proceso ETL completado con éxito! Base de datos inicializada y poblada.")

if __name__ == '__main__':
    process_and_load()
