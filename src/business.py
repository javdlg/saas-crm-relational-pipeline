import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models
from models import Base, SalesRep, Company, Employee

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = f"sqlite:///{os.path.join(DB_DIR, 'crm_custom.db')}"

class CRMManager:
    """
    Manager class to handle CRM business logic.
    Connects to the SQLite database and provides analytical methods.
    """
    def __init__(self, db_path=DB_PATH):
        # Allow connection string injection for testing, defaults to the project DB
        self.engine = create_engine(db_path)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_session(self):
        """Returns the active SQLAlchemy session."""
        return self.session

    def calculate_rep_performance(self):
        """
        Calculates performance for each sales representative based on:
        - Number of managed companies
        - Total annual revenue of 'Active' companies
        - Total number of active employees (contacts) they manage
        Returns a Pandas DataFrame.
        """
        query = """
        SELECT 
            sr.name AS sales_rep,
            COUNT(DISTINCT c.id) AS total_companies,
            SUM(CASE WHEN c.contract_status = 'Active' THEN c.annual_revenue ELSE 0 END) AS active_revenue_m,
            COUNT(DISTINCT e.id) AS total_contacts
        FROM sales_reps sr
        LEFT JOIN companies c ON sr.id = c.sales_rep_id
        LEFT JOIN employees e ON sr.id = e.owner_rep_id
        GROUP BY sr.id
        ORDER BY active_revenue_m DESC;
        """
        df = pd.read_sql_query(query, self.engine)
        return df

    def calculate_contact_scoring(self):
        """
        Assigns a score to each contact based on:
        - influence_score (50% weight)
        - campaign_response_rate (30% weight)
        - decision_maker_flag ('Yes' adds 20 points)
        Returns a Pandas DataFrame.
        """
        query = """
        SELECT 
            e.employee_id,
            e.name,
            e.job_title,
            c.company_id,
            c.industry,
            e.influence_score,
            e.campaign_response_rate,
            e.decision_maker_flag,
            sr.name AS owner_rep
        FROM employees e
        LEFT JOIN companies c ON e.company_id_fk = c.id
        LEFT JOIN sales_reps sr ON e.owner_rep_id = sr.id
        """
        df = pd.read_sql_query(query, self.engine)
        
        # Handle nulls
        df['influence_score'] = df['influence_score'].fillna(0)
        df['campaign_response_rate'] = df['campaign_response_rate'].fillna(0)
        
        # Calculate base score (Max 80 points from these two, assuming they are 0-100 scales)
        df['score'] = (df['influence_score'] * 0.5) + (df['campaign_response_rate'] * 0.3)
        
        # Add 20 points for decision makers
        df.loc[df['decision_maker_flag'].str.lower() == 'yes', 'score'] += 20
        
        # Ensure max 100
        df['score'] = df['score'].clip(upper=100).round(2)
        
        # Sort by top score
        df = df.sort_values(by='score', ascending=False).reset_index(drop=True)
        return df

    def identify_at_risk_accounts(self):
        """
        Identifies companies at risk of churning.
        Criteria: contract_status in ('Pending', 'Expired') AND days_since_last_purchase > 90
        OR frequency_of_purchase is 'Rarely'
        Returns a Pandas DataFrame.
        """
        query = """
        SELECT 
            c.company_id,
            c.industry,
            c.contract_status,
            c.days_since_last_purchase,
            c.frequency_of_purchase,
            c.annual_revenue,
            sr.name AS sales_rep
        FROM companies c
        LEFT JOIN sales_reps sr ON c.sales_rep_id = sr.id
        WHERE (c.contract_status IN ('Pending', 'Expired') AND c.days_since_last_purchase > 90)
           OR c.frequency_of_purchase = 'Rarely'
        ORDER BY c.days_since_last_purchase DESC;
        """
        df = pd.read_sql_query(query, self.engine)
        return df


if __name__ == '__main__':
    # Test the CRM Manager logic
    print("Iniciando CRM Manager...")
    try:
        manager = CRMManager()
        
        print("\n--- Top 5 Sales Reps by Performance ---")
        rep_df = manager.calculate_rep_performance()
        print(rep_df.head())
        
        print("\n--- Top 5 Contacts by Score ---")
        score_df = manager.calculate_contact_scoring()
        print(score_df[['name', 'job_title', 'score', 'owner_rep']].head())
        
        print("\n--- Top 5 At-Risk Accounts ---")
        risk_df = manager.identify_at_risk_accounts()
        print(risk_df.head())
        
        print("\n[OK] Lógica de negocio ejecutada correctamente.")
    except Exception as e:
        print(f"Error al ejecutar CRMManager: {e}")
