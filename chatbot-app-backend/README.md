# MUFG Financial Assistant API Documentation

## Overview
The MUFG Financial Assistant API provides comprehensive user profile management, enhanced chat capabilities with vector search, and stock prediction functionality with database integration.

## Features
- **User Profile Management**: Create, read, update, delete user profiles
- **Enhanced Chat**: LLM-powered chat with vector search and context
- **Stock Predictions**: ML-powered stock predictions with history tracking
- **Database Integration**: SQLite database with chat history and analytics
- **Vector Search**: FAISS-based semantic search for financial recommendations

## Quick Start

### 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run startup script
python startup.py
```

### 2. Start the API Server
```bash
# Development mode (auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Access the API
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### User Profile Management

#### Create User Profile
```http
POST /api/profiles
Content-Type: application/json

{
  "user_id": "user123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "age": 30,
  "country": "Australia",
  "annual_income": 75000,
  "risk_tolerance": "moderate",
  "investment_experience": "intermediate",
  "retirement_target_age": 65
}
```

#### Get User Profile
```http
GET /api/profiles/{user_id}
```

#### Update User Profile
```http
PUT /api/profiles/{user_id}
Content-Type: application/json

{
  "age": 31,
  "annual_income": 80000
}
```

#### Get Profile Completeness
```http
GET /api/profiles/{user_id}/completeness
```

#### Search Profiles
```http
POST /api/profiles/search
Content-Type: application/json

{
  "country": "Australia",
  "age_min": 25,
  "age_max": 40,
  "risk_tolerance": "moderate"
}
```

### Enhanced Chat APIs

#### Enhanced Chat with Database Integration
```http
POST /api/chat/enhanced
Content-Type: application/json

{
  "user_id": "user123",
  "message": "What are good investment options for my profile?",
  "session_id": "session456",
  "include_context": true,
  "save_to_history": true
}
```

#### Enhanced Explain (LLM2)
```http
POST /api/chat/explain
Content-Type: application/json

{
  "user_id": "user123",
  "message": "Explain the risks of growth funds",
  "session_id": "session456",
  "save_to_history": true
}
```

#### Get Chat History
```http
GET /api/chat/history/{user_id}?session_id=session456&limit=50
```

### Stock Prediction APIs

#### Predict Stock Performance
```http
POST /predict-stock?user_id=user123
Content-Type: application/json

{
  "symbol": "AAPL",
  "years": 2
}
```

#### Get User's Prediction History
```http
GET /api/predictions/{user_id}?symbol=AAPL&limit=20
```

#### Get Prediction Analytics
```http
GET /api/predictions/{user_id}/analytics
```

### Legacy Chat APIs (Backward Compatibility)

#### Original Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Hello",
  "userData": {
    "age": 30,
    "country": "Australia"
  }
}
```

#### Original Explain
```http
POST /explain
Content-Type: application/json

{
  "message": "Explain investment strategies",
  "userData": {}
}
```

## Database Schema

### UserProfile Table
- **id**: Primary key
- **user_id**: Unique user identifier
- **Personal Info**: first_name, last_name, email, country, age, gender
- **Financial Info**: annual_income, current_savings, contribution_rate, employment_status
- **Investment Profile**: investment_experience, risk_tolerance, investment_goals, retirement_target_age
- **Current Holdings**: current_fund_type, current_fund_name
- **Preferences**: preferred_communication, newsletter_subscription
- **Metadata**: created_at, updated_at, is_active

### ChatHistory Table
- **id**: Primary key
- **user_id**: User identifier
- **session_id**: Chat session identifier
- **user_message**: User's message
- **bot_response**: Bot's response
- **llm_model**: Which LLM was used (LLM1/LLM2)
- **user_data_snapshot**: JSON snapshot of user data
- **vector_search_results**: JSON of search results
- **created_at**: Timestamp
- **response_time_ms**: Response time in milliseconds

### StockPrediction Table
- **id**: Primary key
- **user_id**: User identifier
- **symbol**: Stock symbol
- **prediction_years**: Prediction timeframe
- **Prediction Results**: current_price, predicted_price, total_return, annualized_return, volatility, max_drawdown
- **Model Info**: model_version, prediction_confidence
- **created_at**: Timestamp

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./mufg_financial.db

# API Keys
OPENAI_API_KEY=your_openai_api_key

# Application Settings
APP_NAME=MUFG Financial Assistant
APP_VERSION=1.0.0
DEBUG=True

# Vector Database Settings
VECTOR_DB_PATH=./vector_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Chat Settings
MAX_CHAT_HISTORY=50
DEFAULT_SESSION_TIMEOUT=3600

# Stock Prediction Settings
MODEL_PATH=../Share_Prediction.h5
LOOKBACK_PERIOD=60
TRADING_DAYS_PER_YEAR=252
```

## Testing

Run the test suite to verify everything is working:

```bash
python test_api.py
```

The test suite will check:
- Database connection
- CRUD operations
- Vector database functionality
- LLM integration
- API endpoints (if server is running)

## Example Usage with Python

```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Create user profile
        profile_data = {
            "user_id": "test123",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "age": 28,
            "annual_income": 65000,
            "risk_tolerance": "moderate"
        }
        
        response = await client.post(
            "http://localhost:8000/api/profiles",
            json=profile_data
        )
        print("Profile created:", response.json())
        
        # Enhanced chat
        chat_data = {
            "user_id": "test123",
            "message": "What investment strategy do you recommend for me?",
            "include_context": True,
            "save_to_history": True
        }
        
        response = await client.post(
            "http://localhost:8000/api/chat/enhanced",
            json=chat_data
        )
        print("Chat response:", response.json())

# Run the test
asyncio.run(test_api())
```

## Frontend Integration

For the React frontend, update your ActionProvider.js to use the enhanced APIs:

```javascript
// Enhanced chat integration
const handleEnhancedChat = async (message, userId) => {
  try {
    const response = await fetch('http://localhost:8000/api/chat/enhanced', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        message: message,
        include_context: true,
        save_to_history: true
      })
    });
    
    const data = await response.json();
    return data.reply;
  } catch (error) {
    console.error('Chat error:', error);
    return 'Sorry, I encountered an error.';
  }
};
```

## Production Deployment

1. **Environment Setup**:
   - Set `DEBUG=False` in production
   - Use PostgreSQL instead of SQLite for better performance
   - Configure proper logging

2. **Database Migration**:
   ```bash
   # Initialize Alembic (if needed)
   alembic init alembic
   
   # Create migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migration
   alembic upgrade head
   ```

3. **Server Deployment**:
   ```bash
   # Install production server
   pip install gunicorn
   
   # Run with gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

## Support

For issues or questions, check:
1. The test suite output (`python test_api.py`)
2. Server logs in the console
3. Interactive API documentation at `/docs`
4. Health check endpoint at `/api/health`
