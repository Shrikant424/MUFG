from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from database import UserProfile, ChatHistory, StockPrediction
from schemas import (
    UserProfileCreate, UserProfileUpdate, SearchFilters,
    InvestmentExperience, RiskTolerance, EmploymentStatus
)

class UserProfileCRUD:
    @staticmethod
    def create_profile(db: Session, profile_data: UserProfileCreate) -> UserProfile:
        """Create a new user profile"""
        # Check if user already exists
        existing_user = db.query(UserProfile).filter(
            UserProfile.user_id == profile_data.user_id
        ).first()
        
        if existing_user:
            raise ValueError(f"User with ID {profile_data.user_id} already exists")
        
        # Check email uniqueness if provided
        if profile_data.email:
            existing_email = db.query(UserProfile).filter(
                UserProfile.email == profile_data.email
            ).first()
            if existing_email:
                raise ValueError(f"Email {profile_data.email} is already registered")
        
        db_profile = UserProfile(**profile_data.dict())
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

    @staticmethod
    def get_profile_by_user_id(db: Session, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user_id"""
        return db.query(UserProfile).filter(
            and_(UserProfile.user_id == user_id, UserProfile.is_active == True)
        ).first()

    @staticmethod
    def get_profile_by_email(db: Session, email: str) -> Optional[UserProfile]:
        """Get user profile by email"""
        return db.query(UserProfile).filter(
            and_(UserProfile.email == email, UserProfile.is_active == True)
        ).first()

    @staticmethod
    def update_profile(db: Session, user_id: str, profile_data: UserProfileUpdate) -> Optional[UserProfile]:
        """Update user profile"""
        db_profile = UserProfileCRUD.get_profile_by_user_id(db, user_id)
        if not db_profile:
            return None
        
        # Check email uniqueness if being updated
        if profile_data.email and profile_data.email != db_profile.email:
            existing_email = db.query(UserProfile).filter(
                and_(
                    UserProfile.email == profile_data.email,
                    UserProfile.user_id != user_id
                )
            ).first()
            if existing_email:
                raise ValueError(f"Email {profile_data.email} is already registered")
        
        # Update fields
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        
        db_profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_profile)
        return db_profile

    @staticmethod
    def delete_profile(db: Session, user_id: str) -> bool:
        """Soft delete user profile"""
        db_profile = UserProfileCRUD.get_profile_by_user_id(db, user_id)
        if not db_profile:
            return False
        
        db_profile.is_active = False
        db_profile.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def search_profiles(
        db: Session, 
        filters: SearchFilters, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserProfile]:
        """Search profiles with filters"""
        query = db.query(UserProfile).filter(UserProfile.is_active == True)
        
        if filters.country:
            query = query.filter(UserProfile.country.ilike(f"%{filters.country}%"))
        
        if filters.age_min is not None:
            query = query.filter(UserProfile.age >= filters.age_min)
        
        if filters.age_max is not None:
            query = query.filter(UserProfile.age <= filters.age_max)
        
        if filters.risk_tolerance:
            query = query.filter(UserProfile.risk_tolerance == filters.risk_tolerance.value)
        
        if filters.investment_experience:
            query = query.filter(UserProfile.investment_experience == filters.investment_experience.value)
        
        if filters.employment_status:
            query = query.filter(UserProfile.employment_status == filters.employment_status.value)
        
        if filters.income_min is not None:
            query = query.filter(UserProfile.annual_income >= filters.income_min)
        
        if filters.income_max is not None:
            query = query.filter(UserProfile.annual_income <= filters.income_max)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_profile_completeness(db: Session, user_id: str) -> Dict[str, Any]:
        """Calculate profile completeness"""
        profile = UserProfileCRUD.get_profile_by_user_id(db, user_id)
        if not profile:
            return {"error": "Profile not found"}
        
        # Define important fields
        important_fields = [
            'first_name', 'last_name', 'email', 'country', 'age', 'gender',
            'annual_income', 'employment_status', 'investment_experience',
            'risk_tolerance', 'retirement_target_age', 'current_fund_type'
        ]
        
        completed_fields = []
        missing_fields = []
        
        for field in important_fields:
            value = getattr(profile, field)
            if value is not None and value != "":
                completed_fields.append(field)
            else:
                missing_fields.append(field)
        
        completeness_percentage = (len(completed_fields) / len(important_fields)) * 100
        
        # Generate recommendations based on missing fields
        recommendations = []
        if 'annual_income' in missing_fields:
            recommendations.append("Add your annual income for better investment recommendations")
        if 'risk_tolerance' in missing_fields:
            recommendations.append("Complete risk assessment for personalized advice")
        if 'retirement_target_age' in missing_fields:
            recommendations.append("Set your retirement target age for goal planning")
        
        # Calculate profile score
        profile_score = completeness_percentage
        if profile.investment_experience and profile.risk_tolerance:
            profile_score += 10  # Bonus for complete investment profile
        
        return {
            "completeness_percentage": completeness_percentage,
            "missing_fields": missing_fields,
            "completed_fields": completed_fields,
            "profile_score": min(profile_score, 100),
            "recommendations": recommendations
        }

class ChatHistoryCRUD:
    @staticmethod
    def save_chat(
        db: Session,
        user_id: str,
        user_message: str,
        bot_response: str,
        llm_model: str = None,
        session_id: str = None,
        user_data: Dict = None,
        vector_results: List = None,
        response_time_ms: int = None
    ) -> ChatHistory:
        """Save chat interaction to history"""
        db_chat = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            llm_model=llm_model,
            user_data_snapshot=json.dumps(user_data) if user_data else None,
            vector_search_results=json.dumps(vector_results) if vector_results else None,
            response_time_ms=response_time_ms
        )
        
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat

    @staticmethod
    def get_chat_history(
        db: Session,
        user_id: str,
        session_id: str = None,
        limit: int = 50
    ) -> List[ChatHistory]:
        """Get chat history for user"""
        query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)
        
        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)
        
        return query.order_by(desc(ChatHistory.created_at)).limit(limit).all()

    @staticmethod
    def get_recent_context(db: Session, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent chat context for LLM"""
        recent_chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(desc(ChatHistory.created_at)).limit(limit).all()
        
        context = []
        for chat in reversed(recent_chats):  # Reverse to get chronological order
            context.extend([
                {"role": "user", "content": chat.user_message},
                {"role": "assistant", "content": chat.bot_response}
            ])
        
        return context

class StockPredictionCRUD:
    @staticmethod
    def save_prediction(
        db: Session,
        user_id: str,
        symbol: str,
        prediction_years: int,
        prediction_data: Dict,
        model_version: str = "v1.0",
        confidence: float = None
    ) -> StockPrediction:
        """Save stock prediction"""
        stats = prediction_data.get('stats', {})
        
        db_prediction = StockPrediction(
            user_id=user_id,
            symbol=symbol.upper(),
            prediction_years=prediction_years,
            current_price=stats.get('current_price'),
            predicted_price=stats.get('final_price'),
            total_return=stats.get('total_return'),
            annualized_return=stats.get('annualized_return'),
            volatility=stats.get('volatility'),
            max_drawdown=stats.get('max_drawdown'),
            model_version=model_version,
            prediction_confidence=confidence
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction

    @staticmethod
    def get_user_predictions(
        db: Session,
        user_id: str,
        symbol: str = None,
        limit: int = 20
    ) -> List[StockPrediction]:
        """Get user's stock predictions"""
        query = db.query(StockPrediction).filter(StockPrediction.user_id == user_id)
        
        if symbol:
            query = query.filter(StockPrediction.symbol == symbol.upper())
        
        return query.order_by(desc(StockPrediction.created_at)).limit(limit).all()

    @staticmethod
    def get_prediction_analytics(db: Session, user_id: str) -> Dict[str, Any]:
        """Get analytics for user's predictions"""
        predictions = db.query(StockPrediction).filter(
            StockPrediction.user_id == user_id
        ).all()
        
        if not predictions:
            return {"total_predictions": 0}
        
        total_predictions = len(predictions)
        avg_return = sum(p.annualized_return for p in predictions if p.annualized_return) / total_predictions
        avg_volatility = sum(p.volatility for p in predictions if p.volatility) / total_predictions
        
        symbols_analyzed = list(set(p.symbol for p in predictions))
        
        return {
            "total_predictions": total_predictions,
            "average_return": avg_return,
            "average_volatility": avg_volatility,
            "symbols_analyzed": symbols_analyzed,
            "prediction_frequency": len(predictions) / max((datetime.now() - predictions[-1].created_at).days, 1)
        }

# Utility functions
def get_user_data_dict(profile: UserProfile) -> Dict[str, Any]:
    """Convert UserProfile to dictionary for LLM context"""
    if not profile:
        return {}
    
    return {
        "user_id": profile.user_id,
        "country": profile.country,
        "age": profile.age,
        "gender": profile.gender,
        "annual_income": profile.annual_income,
        "current_savings": profile.current_savings,
        "contribution_rate": profile.contribution_rate,
        "employment_status": profile.employment_status,
        "investment_experience": profile.investment_experience,
        "risk_tolerance": profile.risk_tolerance,
        "investment_goals": profile.investment_goals,
        "retirement_target_age": profile.retirement_target_age,
        "current_fund_type": profile.current_fund_type,
        "current_fund_name": profile.current_fund_name
    }
