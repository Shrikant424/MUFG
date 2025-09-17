# Superannuation Advisory Platform - PensionPal


A comprehensive financial advisory platform that combines traditional investment recommendations with machine learning-powered predictions and LLM integration to help users optimize their superannuation (retirement savings) strategy.


## Table of Contents


1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Technology Stack](#technology-stack)
4. [Setup & Installation](#setup--installation)
5. [User Journey Walkthrough](#user-journey-walkthrough)
6. [Component Breakdown](#component-breakdown)
7. [LLM Integration](#llm-integration)
8. [ML Model Integration](#ml-model-integration)


---


## Project Overview


### What This Platform Does
This is an AI-powered superannuation (retirement savings) advisory platform that provides:


- **Personalized Financial Advisory and Predictions**: LLM-powered conversational AI for retirement planning
- **ML-Powered Insights**: According to the user data provided , the model is trained and insights are established.
- **Investment Recommendations**: Risk-based asset allocation suggestions
- **Interactive Dashboard**: Real-time portfolio tracking and analysis
- **Educational Chat Interface ( Chat bot )**: AI advisor for financial literacy


### Key Features
- User authentication and profile management
- ML-driven retirement projections
- LLM-powered financial advisory chat
- Real-time dashboard with predictions
- Portfolio optimization recommendations
- Risk assessment and scenario planning
- Chat-bot answering interface


---


## Project Structure


```
MUFG/
│
├── chatbot-app/ # Frontend (React + Vite)
│ │
│ ├── src/ # Application source
│ │ │
│ │ ├── chatbot/ # Chatbot module
│ │ │ ├── components/ # Reusable UI components
│ │ │ │ ├── MarkdownMessage.jsx
│ │ │ │ ├── SimpleStockWidget.jsx
│ │ │ │ ├── StockChart.jsx
│ │ │ │ ├── StockChart.css
│ │ │ │ ├── StockChartModal.jsx
│ │ │ │ └── StockChartModal.css
│ │ │ │
│ │ │ ├── services/ # Service layer for chatbot
│ │ │ │ ├── TypingIndicator.jsx
│ │ │ │ └── TypingIndicator.css
│ │ │ │
│ │ │ ├── utils/ # Utility functions
│ │ │ │ └── spellCorrection.js
│ │ │ ├── ActionProvider.js
│ │ │ ├── Config.jsx
│ │ │ ├── LLMService.js
│ │ │ ├── MessageParser.js
│ │ │ ├── ChatbotPage.jsx # Chatbot entry page
│ │ │ └── ChatPage.css
│ │ │
│ │ ├── services/ # Shared API services
│ │ │ └── api.js
│ │ │
│ │ ├── App.jsx # Root component
│ │ ├── App.css
│ │ ├── AuthPage.jsx # Login/Authentication page
│ │ ├── Dashboard.jsx # Main dashboard
│ │ ├── SignupForm.jsx # User signup form
│ │ ├── UserDataForm.jsx # User data input form
│ │ ├── StockPredictionChart.jsx # Stock prediction visualization
│ │ ├── ChartModal.jsx # Chart modal popup
│ │ ├── index.css
│ │ ├── index.html
│ │ └── main.jsx # React entry point
│ │
│ ├── package.json # Dependencies
│ ├── package-lock.json
│ ├── vite.config.js # Vite configuration
│ ├── eslint.config.js # ESLint configuration
│ └── README.md # Frontend documentation
│
├── chatbot-app-backend/ # Backend (Python + ML)
│ ├── LLM/ # Large Language Model scripts
│ │ ├── LLM1.py
│ │ └── LLM2.py
│ │ └── LLM3.py
│ │ └── context_manager.py
│ ├── models/ # ML model artifacts
│ │ ├── feature_columns.joblib
│ │ ├── label_encoders.joblib
│ │ ├── model_metadata.joblib
│ │ ├── pension_model.joblib
│ │ ├── return_model.joblib
│ │ ├── scaler.joblib
│ │ └── models.zip
│ │
│ ├── Share_Prediction.h5 # Trained Keras model
│ ├── super_annuation_data.xlsx # Dataset
│ ├── tales.sql # Database schema
│ ├── extract_stock_symbols.py # Data extraction script
│ ├── preprocessors.py # Data preprocessing utilities
│ ├── predict_price.py # Stock price prediction script
│ ├── train_model.py # Model training
│ ├── model.py # Model definition
│ ├── main.py # Backend entry point (API server)
│ ├── requirements.txt # Python dependencies
│ ├── .env # Environment variables
│ ├── .gitignore
│ ├── CHART_SETUP_GUIDE.md # Chart setup instructions
│ └── README.MD # Backend documentation
│
└── .git/ # Git version control


```


---


## Technology Stack


### Frontend
- **Framework**: React.js + Vite
- **Styling**: css + javascript
- **HTTP Client**: Fast API
- **State Management**: React Hooks (useState, useEffect)


### Backend Services
- **Main API Server**: FastAPI (Port 8000)
- **ML/LLM Server**: Python/FastAPI (Port 8000)


### AI/ML Integration
- **Machine Learning**: Python (scikit-learn, pandas, numpy)
- **LLM Integration**: OpenAI API / mistral / deepseek
- **Prediction Models**: Custom regression and classification models for superannuation forecasting


### Database & Storage
- **Profile Storage**: MySQL Database
- **Chat History**: Persistent storage with user context
- **Caching**: Local storage for client-side caching


---


## Setup & Installation


### Prerequisites
```bash
- Python (v3.8 or higher)
- React (v20)
- npm or yarn package manager
- OpenAI API key (for LLM features)
- My SQL-Workbench - 5.0+
```


### 1. Clone and Setup Frontend
```bash
# Clone the repository
git clone <repository-url>
cd chatbot-app


# Install frontend dependencies
npm install


# Start the development server
npm run dev
```


### 2. Setup Main API Server (Node.js)
```bash
# Navigate to backend directory
cd chatbot-app-backend


# Create virtual environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate


# Install dependencies
pip install -r “requirements.txt”


# Start the server
uvicorn main:app --reload --port 8000


```


---


## User Journey Walkthrough

### Step 1: Authentication Flow
The application starts with the Login Page component:


**User Experience:**
1. User visits the application
2. Presented with login/signup form
3. Enters credentials (username/password)
4. System authenticates via ML server (`/login` or `/signup`)
5. On success, redirected to dashboard
---

### Step 2: Profile Setup (First Time Users)

New users are redirected to **UserDataForm**:


**User Experience:**
1. Complete financial profile questionnaire
2. Data includes demographics, income, savings, goals
3. Risk tolerance assessment
4. Profile saved to ML server (`/profile/{username}`)
---

### Step 3: Dashboard Experience
The **DashboardPage** is the main hub:


**Key Dashboard Elements:**
1. **Header**: User info, navigation, logout
2. **Stats Cards**: Current savings, years to retirement, income, risk profile
3. **Retirement Progress**: Visual progress tracker
4. **AI Predictions**: ML-powered retirement projections
5. **Portfolio Performance**: Risk/return analysis
6. **Contribution Strategy**: Personalized recommendations
---
### Step 4: AI Chat Interface
Users can access the **ChatPage** for personalized advice:


**Features:**
- LLM-powered financial advisor
- Context-aware conversations
- Profile-based recommendations
- Chat history persistence
---

## Component Breakdown


### Core Application Components


#### 1. App.jsx - Main Application Route


**Responsibilities:**
- Route management and navigation
- User authentication state
- Profile data management
- Automatic profile fetching
---  
#### 2. AuthPage Component
**File Location**: `src/AuthPage.jsx`


**Features:**
- Login/signup toggle
- Form validation
- Error handling and user feedback
---

#### 3. UserDataForm Component
**File Location**: `src/UserDataForm.jsx`


**Features:**
- Comprehensive financial profile form
- Multi-step form progression
- Profile completion tracking
---
#### 4. DashboardPage Component
**File Location**: `src/Dashboard.js`


**Key Features:**
- **Stats Cards**: Financial overview with icons and metrics
- **Retirement Progress**: Visual timeline with milestones
- **Portfolio Performance**: Risk/return visualization
- **Contribution Strategy**: Personalized optimization

**UI Components:**
- Responsive grid layout
- Interactive progress bars
- Color-coded risk indicators
- Currency and percentage formatters
---
#### 5. ChatPage Component
**File Location**: `src/chatbot/ChatbotPage.js`


**Features:**
- LLM-powered conversational interface
- Context-aware responses
- Chat history persistence
- Profile-based recommendations


---
## LLM Integration
### Implementation Architecture
The platform integrates Large Language Models for conversational financial advice:
### Context Awareness
The LLM maintains context through:
- **User Profile Integration**: All advice considers individual circumstances
- **Chat History**: Maintains conversation context across sessions
- **Prediction Integration**: References ML model outputs in responses
- **Regulatory Knowledge**: Australian superannuation rules and regulations


### Chat Features
1. **Profile-Based Advice**: Responses tailored to user's financial situation
2. **Scenario Analysis**: Can explain ML predictions and scenarios
3. **Educational Content**: Financial literacy and concept explanations
4. **Action Planning**: Specific steps and recommendations


---

## ML Model Integration


### Prediction Models

The platform uses custom ML models for:
1. **Retirement Balance Prediction**
   - Features: age, income, current savings, risk tolerance
   - Algorithm: Random Forest Regression
   - Output: Projected final balance with confidence intervals
---

2. **Risk Assessment**
   - Portfolio volatility estimation
   - Risk-return optimization
   - Suitability scoring
---

3. **Contribution Optimization**
   - Monthly contribution recommendations
   - Tax efficiency analysis
   - Target income scenarios

## Security Implementation


### Data Protection - Upcoming Changes
- Input validation and sanitization
- Secure password hashing (bcrypt)
- CORS configuration for API endpoints
- Environment variable management for secrets


### Privacy Considerations - Upcoming Changes
- User data encryption at rest
- Limited data retention policies
- Anonymized analytics
- Consent management for data usage


---
## Contributing
### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Make changes with proper testing
4. Commit with descriptive messages
5. Push and create Pull Request

### Code Standards
- ESLint configuration for JavaScript
- Black formatting for Python
- Comprehensive error handling
- Unit test coverage >80%
- Documentation for all API endpoints

```bash
**Built with React, Python, and AI for smarter retirement planning** 🚀
```
