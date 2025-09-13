from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any
from openai import OpenAI  # or the DeepSeek client
from LLM.LLM1 import callLLM1
from LLM.LLM2 import callLLM2
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from datetime import datetime, timedelta
import os
import uuid
from sqlalchemy.orm import Session

# Database imports
from database import get_db, init_db, UserProfile, ChatHistory, StockPrediction
from schemas import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    ChatHistoryResponse, StockPredictionResponse, ProfileSummary,
    SearchFilters, APIResponse, EnhancedChatMessage, ChatMessage
)
from crud import UserProfileCRUD, ChatHistoryCRUD, StockPredictionCRUD, get_user_data_dict

app = FastAPI(title="MUFG Financial Assistant API", version="1.0.0")

# Initialize database
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # React dev server (Vite)
    allow_credentials=True,
    allow_methods=["*"],   # allow POST, GET, OPTIONS etc.
    allow_headers=["*"],
)

# Load the ML model once at startup
try:
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Share_Prediction.h5')
    stock_model = load_model(model_path)
    print(f"Stock prediction model loaded successfully from {model_path}")
except Exception as e:
    print(f"Error loading model: {e}")
    stock_model = None

class PredictionRequest(BaseModel):
    symbol: str
    years: int = 2

# =============================================================================
# USER PROFILE APIS
# =============================================================================

@app.post("/api/profiles", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(profile_data: UserProfileCreate, db: Session = Depends(get_db)):
    """Create a new user profile"""
    try:
        profile = UserProfileCRUD.create_profile(db, profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")

@app.get("/api/profiles/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Get user profile by user_id"""
    profile = UserProfileCRUD.get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile

@app.put("/api/profiles/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, profile_data: UserProfileUpdate, db: Session = Depends(get_db)):
    """Update user profile"""
    try:
        profile = UserProfileCRUD.update_profile(db, user_id, profile_data)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.delete("/api/profiles/{user_id}", response_model=APIResponse)
async def delete_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Delete user profile (soft delete)"""
    success = UserProfileCRUD.delete_profile(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return APIResponse(
        success=True,
        message=f"User profile {user_id} deleted successfully"
    )

@app.get("/api/profiles/{user_id}/completeness", response_model=ProfileSummary)
async def get_profile_completeness(user_id: str, db: Session = Depends(get_db)):
    """Get profile completeness analysis"""
    completeness_data = UserProfileCRUD.get_profile_completeness(db, user_id)
    if "error" in completeness_data:
        raise HTTPException(status_code=404, detail=completeness_data["error"])
    
    return ProfileSummary(
        user_id=user_id,
        **completeness_data
    )

@app.post("/api/profiles/search", response_model=List[UserProfileResponse])
async def search_user_profiles(
    filters: SearchFilters,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search user profiles with filters"""
    try:
        profiles = UserProfileCRUD.search_profiles(db, filters, skip, limit)
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# =============================================================================
# ENHANCED CHAT APIS WITH DATABASE INTEGRATION
# =============================================================================

@app.post("/api/chat/enhanced")
async def enhanced_chat(request: EnhancedChatMessage, db: Session = Depends(get_db)):
    """Enhanced chat with database integration and context"""
    start_time = datetime.now()
    
    try:
        # Get user profile for context
        user_profile = UserProfileCRUD.get_profile_by_user_id(db, request.user_id)
        user_data = get_user_data_dict(user_profile) if user_profile else {}
        
        # Get recent chat context if requested
        context = []
        if request.include_context:
            context = ChatHistoryCRUD.get_recent_context(db, request.user_id, limit=3)
        
        # Handle special commands
        msg = request.message.lower().strip()
        if msg in ["profile", "show my data", "show my profile"]:
            if user_data:
                profile_str = "\\n".join([f"{k}: {v}" for k, v in user_data.items() if v is not None])
                response = f"Your profile:\\n{profile_str}"
            else:
                response = "No user profile data found. Please create your profile first."
        else:
            # Call LLM with enhanced context
            response = callLLM1(request.message, user_data)
        
        # Calculate response time
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Save to chat history if requested
        if request.save_to_history:
            ChatHistoryCRUD.save_chat(
                db=db,
                user_id=request.user_id,
                user_message=request.message,
                bot_response=response,
                llm_model="LLM1",
                session_id=request.session_id,
                user_data=user_data,
                response_time_ms=response_time
            )
        
        return {
            "reply": response,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "response_time_ms": response_time,
            "context_used": len(context) > 0,
            "profile_available": user_profile is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/api/chat/explain")
async def enhanced_explain(request: EnhancedChatMessage, db: Session = Depends(get_db)):
    """Enhanced explain chat with LLM2"""
    start_time = datetime.now()
    
    try:
        # Get user profile for context
        user_profile = UserProfileCRUD.get_profile_by_user_id(db, request.user_id)
        user_data = get_user_data_dict(user_profile) if user_profile else {}
        
        # Call LLM2
        response = callLLM2(request.message, user_data)
        
        # Calculate response time
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Save to chat history if requested
        if request.save_to_history:
            ChatHistoryCRUD.save_chat(
                db=db,
                user_id=request.user_id,
                user_message=request.message,
                bot_response=response,
                llm_model="LLM2",
                session_id=request.session_id,
                user_data=user_data,
                response_time_ms=response_time
            )
        
        return {
            "reply": response,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "response_time_ms": response_time,
            "profile_available": user_profile is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explain processing failed: {str(e)}")

@app.get("/api/chat/history/{user_id}", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    user_id: str,
    session_id: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for user"""
    try:
        history = ChatHistoryCRUD.get_chat_history(db, user_id, session_id, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")

# =============================================================================
# ORIGINAL CHAT APIS (BACKWARD COMPATIBILITY)
# =============================================================================

@app.post("/chat")
def chat(request: ChatMessage):
    """Original chat endpoint for backward compatibility"""
    # If user asks for profile or to show data, return userData directly
    msg = request.message.lower().strip()
    if msg in ["profile", "show my data", "show my profile"]:
        if request.userData:
            profile_str = "\\n".join([f"{k}: {v}" for k, v in request.userData.items()])
            return {"reply": f"Your profile:\\n{profile_str}"}
        else:
            return {"reply": "No user profile data found."}
    # Otherwise, pass userData to LLM1 if needed
    response = callLLM1(request.message, request.userData)
    return {"reply": response}

@app.post("/explain")
def explain(request: ChatMessage):
    """Original explain endpoint for backward compatibility"""
    response = callLLM2(request.message, request.userData)
    return {"reply": response}

# =============================================================================
# STOCK PREDICTION APIS WITH DATABASE INTEGRATION
# =============================================================================

# Stock prediction functions
def get_stock_data(symbol, start_date, end_date):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

def prepare_data(stock_data, lookback_period=60):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(stock_data['Close'].values.reshape(-1, 1))
    return scaler

def predict_future_years_realistic(model, stock_data, scaler, years=2, lookback_period=60):
    last_sequence = stock_data['Close'].values[-lookback_period:]
    last_sequence_scaled = scaler.transform(last_sequence.reshape(-1, 1))
    
    trading_days_per_year = 252
    total_days = years * trading_days_per_year
    
    last_date = stock_data.index[-1]
    future_dates = pd.bdate_range(start=last_date + timedelta(days=1), periods=total_days)
    
    predictions = []
    current_sequence = last_sequence_scaled.flatten()
    
    # Calculate historical volatility
    historical_returns = np.diff(np.log(stock_data['Close'].values[-252:]))
    daily_volatility = np.std(historical_returns)
    
    for i in range(total_days):
        input_sequence = current_sequence[-lookback_period:].reshape(1, lookback_period, 1)
        next_pred_scaled = model.predict(input_sequence, verbose=0)
        next_pred = scaler.inverse_transform(next_pred_scaled)[0][0]
        
        # Add realistic volatility
        if i > 0:
            random_return = np.random.normal(0, daily_volatility)
            volatility_adjustment = next_pred * random_return
            next_pred = next_pred + volatility_adjustment
            
            prev_price = predictions[-1] if predictions else stock_data['Close'].iloc[-1]
            max_change = prev_price * 0.2
            next_pred = np.clip(next_pred, prev_price - max_change, prev_price + max_change)
            next_pred = max(next_pred, prev_price * 0.5)
        
        predictions.append(next_pred)
        next_pred_scaled = scaler.transform([[next_pred]])[0][0]
        current_sequence = np.append(current_sequence, next_pred_scaled)
    
    return future_dates, np.array(predictions)

@app.post("/predict-stock")
async def predict_stock(request: PredictionRequest, user_id: str = None, db: Session = Depends(get_db)):
    """Stock prediction with optional database storage"""
    if stock_model is None:
        raise HTTPException(status_code=500, detail="Stock prediction model not loaded")
    
    try:
        # Fetch historical data
        current_date = datetime.now()
        start_date = (current_date - timedelta(days=3*365 + 120)).strftime("%Y-%m-%d")
        end_date = current_date.strftime("%Y-%m-%d")
        
        stock_data = get_stock_data(request.symbol, start_date, end_date)
        
        if stock_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the given symbol")
        
        # Prepare data
        scaler = prepare_data(stock_data)
        
        # Make predictions
        future_dates, future_predictions = predict_future_years_realistic(
            stock_model, stock_data, scaler, request.years
        )
        
        # Get historical data for chart (last 2 years)
        historical_cutoff = datetime.now() - timedelta(days=730)
        if stock_data.index.tz is not None:
            historical_cutoff = historical_cutoff.replace(tzinfo=stock_data.index.tz)
        
        historical_mask = stock_data.index >= historical_cutoff
        historical_dates = stock_data.index[historical_mask]
        historical_prices = stock_data['Close'].values[historical_mask]
        
        # Calculate uncertainty bands
        prediction_std = np.std(np.diff(future_predictions)) * np.sqrt(np.arange(len(future_predictions)))
        uncertainty_upper = future_predictions + prediction_std
        uncertainty_lower = future_predictions - prediction_std
        
        # Calculate statistics
        current_price = stock_data['Close'].iloc[-1]
        final_price = future_predictions[-1]
        total_return = ((final_price - current_price) / current_price) * 100
        annualized_return = (((final_price / current_price) ** (1/request.years)) - 1) * 100
        
        # Calculate volatility and max drawdown
        daily_returns = np.diff(future_predictions) / future_predictions[:-1]
        predicted_volatility = np.std(daily_returns) * np.sqrt(252) * 100
        
        cumulative_returns = np.cumprod(1 + daily_returns)
        max_drawdown = np.min(np.minimum.accumulate(cumulative_returns / np.maximum.accumulate(cumulative_returns)) - 1) * 100
        
        prediction_result = {
            "historical_dates": [date.strftime("%Y-%m-%d") for date in historical_dates],
            "historical_prices": historical_prices.tolist(),
            "future_dates": [date.strftime("%Y-%m-%d") for date in future_dates],
            "future_predictions": future_predictions.tolist(),
            "uncertainty_upper": uncertainty_upper.tolist(),
            "uncertainty_lower": uncertainty_lower.tolist(),
            "stats": {
                "current_price": float(current_price),
                "final_price": float(final_price),
                "total_return": float(total_return),
                "annualized_return": float(annualized_return),
                "volatility": float(predicted_volatility),
                "max_drawdown": float(max_drawdown)
            }
        }
        
        # Save prediction to database if user_id provided
        if user_id:
            try:
                StockPredictionCRUD.save_prediction(
                    db=db,
                    user_id=user_id,
                    symbol=request.symbol,
                    prediction_years=request.years,
                    prediction_data=prediction_result,
                    model_version="v1.0"
                )
            except Exception as save_error:
                print(f"Warning: Failed to save prediction to database: {save_error}")
        
        return prediction_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predictions/{user_id}", response_model=List[StockPredictionResponse])
async def get_user_predictions(
    user_id: str,
    symbol: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get user's stock prediction history"""
    try:
        predictions = StockPredictionCRUD.get_user_predictions(db, user_id, symbol, limit)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve predictions: {str(e)}")

@app.get("/api/predictions/{user_id}/analytics")
async def get_prediction_analytics(user_id: str, db: Session = Depends(get_db)):
    """Get analytics for user's prediction history"""
    try:
        analytics = StockPredictionCRUD.get_prediction_analytics(db, user_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    return {
        "message": "MUFG Financial Assistant API is running",
        "version": "1.0.0",
        "features": [
            "User Profile Management",
            "Enhanced Chat with Database Integration",
            "Stock Prediction with History",
            "Vector Search Integration",
            "Chat History Tracking"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "database": "connected",
        "ml_model": "loaded" if stock_model else "not loaded"
    }