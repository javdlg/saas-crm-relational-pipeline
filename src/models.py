# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SalesRep(Base):
    """
    Model representing a sales representative.
    Maps to 'sales_reps' table.
    """
    __tablename__ = 'sales_reps'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    
    # Relationships
    companies = relationship("Company", back_populates="sales_rep")
    employees = relationship("Employee", back_populates="owner_rep")

    def __repr__(self):
        return f"<SalesRep(name='{self.name}')>"


class Company(Base):
    """
    Model representing a B2B company/account.
    Maps to 'companies' table.
    """
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, nullable=False, unique=True) # e.g., C0001
    
    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    annual_revenue = Column(Float, nullable=True) # in M₺
    marketing_spend = Column(Float, nullable=True) # in K₺
    campaign_type = Column(String, nullable=True)
    leads_generated = Column(Integer, nullable=True)
    conversion_rate = Column(Float, nullable=True)
    region = Column(String, nullable=True)
    district = Column(String, nullable=True)
    last_product_1 = Column(String, nullable=True)
    last_product_2 = Column(String, nullable=True)
    frequency_of_purchase = Column(String, nullable=True)
    days_since_last_purchase = Column(Integer, nullable=True)
    contract_status = Column(String, nullable=True)
    total_purchases_last_year = Column(Integer, nullable=True)
    payment_behavior = Column(String, nullable=True)
    preferred_channel = Column(String, nullable=True)
    
    # Foreign Key
    sales_rep_id = Column(Integer, ForeignKey('sales_reps.id'), nullable=True, index=True)
    
    # Relationships
    sales_rep = relationship("SalesRep", back_populates="companies")
    employees = relationship("Employee", back_populates="company")

    def __repr__(self):
        return f"<Company(id='{self.company_id}', industry='{self.industry}')>"


class Employee(Base):
    """
    Model representing an employee/contact at a company.
    Maps to 'employees' table.
    """
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, nullable=False, unique=True) # e.g., E00001
    
    name = Column(String, nullable=True)
    department = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    seniority_level = Column(String, nullable=True)
    education_level = Column(String, nullable=True)
    work_location = Column(String, nullable=True)
    newsletter_subscription = Column(String, nullable=True) # Yes/No
    campaign_response_rate = Column(Float, nullable=True)
    tenure_years = Column(Float, nullable=True)
    event_attendance = Column(Integer, nullable=True)
    influence_score = Column(Float, nullable=True)
    decision_maker_flag = Column(String, nullable=True) # Yes/No
    preferred_contact_method = Column(String, nullable=True)
    language = Column(String, nullable=True)
    last_contact_date = Column(String, nullable=True) # Stored as string or parsed to Date
    next_followup_date = Column(String, nullable=True)
    active_flag = Column(String, nullable=True) # Yes/No
    data_source = Column(String, nullable=True)
    
    # Foreign Keys
    company_id_fk = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    owner_rep_id = Column(Integer, ForeignKey('sales_reps.id'), nullable=True, index=True)
    
    # Relationships
    company = relationship("Company", back_populates="employees")
    owner_rep = relationship("SalesRep", back_populates="employees")

    def __repr__(self):
        return f"<Employee(id='{self.employee_id}', name='{self.name}')>"
