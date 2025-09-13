from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class InvestmentExperience(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class RiskTolerance(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class EmploymentStatus(str, Enum):
    EMPLOYED_FULL_TIME = "employed_full_time"
    EMPLOYED_PART_TIME = "employed_part_time"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"

class FundType(str, Enum):
    GROWTH = "growth"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    INDEX = "index"
    SECTOR_SPECIFIC = "sector_specific"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class CommunicationPreference(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    APP = "app"
    PHONE = "phone"

# Request Models
class UserProfileCreate(BaseModel):
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    country: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    annual_income: Optional[float] = None
    current_savings: Optional[float] = None
    contribution_rate: Optional[float] = None
    employment_status: Optional[EmploymentStatus] = None
    investment_experience: Optional[InvestmentExperience] = None
    risk_tolerance: Optional[RiskTolerance] = None
    investment_goals: Optional[str] = None
    retirement_target_age: Optional[int] = None
    current_fund_type: Optional[FundType] = None
    current_fund_name: Optional[str] = None
    preferred_communication: Optional[CommunicationPreference] = None
    newsletter_subscription: Optional[bool] = True

    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 18 or v > 100):
            raise ValueError('Age must be between 18 and 100')
        return v

    @validator('contribution_rate')
    def validate_contribution_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Contribution rate must be between 0 and 100 percent')
        return v

    @validator('retirement_target_age')
    def validate_retirement_age(cls, v):
        if v is not None and (v < 50 or v > 80):
            raise ValueError('Retirement target age must be between 50 and 80')
        return v

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    country: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    annual_income: Optional[float] = None
    current_savings: Optional[float] = None
    contribution_rate: Optional[float] = None
    employment_status: Optional[EmploymentStatus] = None
    investment_experience: Optional[InvestmentExperience] = None
    risk_tolerance: Optional[RiskTolerance] = None
    investment_goals: Optional[str] = None
    retirement_target_age: Optional[int] = None
    current_fund_type: Optional[FundType] = None
    current_fund_name: Optional[str] = None
    preferred_communication: Optional[CommunicationPreference] = None
    newsletter_subscription: Optional[bool] = None

    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 18 or v > 100):
            raise ValueError('Age must be between 18 and 100')
        return v

    @validator('contribution_rate')
    def validate_contribution_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Contribution rate must be between 0 and 100 percent')
        return v

    @validator('retirement_target_age')
    def validate_retirement_age(cls, v):
        if v is not None and (v < 50 or v > 80):
            raise ValueError('Retirement target age must be between 50 and 80')
        return v

# Response Models
class UserProfileResponse(BaseModel):
    id: int
    user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    country: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    annual_income: Optional[float]
    current_savings: Optional[float]
    contribution_rate: Optional[float]
    employment_status: Optional[str]
    investment_experience: Optional[str]
    risk_tolerance: Optional[str]
    investment_goals: Optional[str]
    retirement_target_age: Optional[int]
    current_fund_type: Optional[str]
    current_fund_name: Optional[str]
    preferred_communication: Optional[str]
    newsletter_subscription: bool
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    id: int
    user_id: str
    session_id: Optional[str]
    user_message: str
    bot_response: str
    llm_model: Optional[str]
    created_at: datetime
    response_time_ms: Optional[int]

    class Config:
        from_attributes = True

class StockPredictionResponse(BaseModel):
    id: int
    user_id: str
    symbol: str
    prediction_years: int
    current_price: Optional[float]
    predicted_price: Optional[float]
    total_return: Optional[float]
    annualized_return: Optional[float]
    volatility: Optional[float]
    max_drawdown: Optional[float]
    model_version: Optional[str]
    prediction_confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

# Utility Models
class ProfileSummary(BaseModel):
    user_id: str
    completeness_percentage: float
    missing_fields: List[str]
    profile_score: float
    recommendations: List[str]

class BulkUpdateRequest(BaseModel):
    updates: List[Dict[str, Any]]
    
class SearchFilters(BaseModel):
    country: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    risk_tolerance: Optional[RiskTolerance] = None
    investment_experience: Optional[InvestmentExperience] = None
    employment_status: Optional[EmploymentStatus] = None
    income_min: Optional[float] = None
    income_max: Optional[float] = None

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = datetime.now()

# Chat Integration Models
class ChatMessage(BaseModel):
    message: str
    userData: dict = {}
    session_id: Optional[str] = None

class EnhancedChatMessage(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None
    include_context: bool = True
    save_to_history: bool = True
