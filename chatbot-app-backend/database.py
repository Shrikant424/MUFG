from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mufg_financial.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Personal Information
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    country = Column(String(100))
    age = Column(Integer)
    gender = Column(String(20))
    
    # Financial Information
    annual_income = Column(Float)
    current_savings = Column(Float)
    contribution_rate = Column(Float)  # Percentage of income
    employment_status = Column(String(100))
    
    # Investment Profile
    investment_experience = Column(String(50))  # beginner, intermediate, advanced
    risk_tolerance = Column(String(50))  # conservative, moderate, aggressive
    investment_goals = Column(Text)
    retirement_target_age = Column(Integer)
    
    # Current Holdings
    current_fund_type = Column(String(100))  # growth, balanced, conservative
    current_fund_name = Column(String(255))
    
    # Preferences
    preferred_communication = Column(String(50))  # email, sms, app
    newsletter_subscription = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    session_id = Column(String(255), index=True)
    
    # Chat Content
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    llm_model = Column(String(50))  # LLM1 or LLM2
    
    # Context
    user_data_snapshot = Column(Text)  # JSON string of user data at time of chat
    vector_search_results = Column(Text)  # JSON string of relevant search results
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    response_time_ms = Column(Integer)  # Response time in milliseconds

class StockPrediction(Base):
    __tablename__ = "stock_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    
    # Stock Information
    symbol = Column(String(20), nullable=False)
    prediction_years = Column(Integer, nullable=False)
    
    # Prediction Results
    current_price = Column(Float)
    predicted_price = Column(Float)
    total_return = Column(Float)
    annualized_return = Column(Float)
    volatility = Column(Float)
    max_drawdown = Column(Float)
    
    # Model Information
    model_version = Column(String(50))
    prediction_confidence = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
