# SuperAI Assistant - AI-Powered Superannuation Investment Advisor

An intelligent chatbot that helps superannuation users make informed investment decisions through personalized recommendations, risk assessment, and educational insights.

## 🌟 Features

- **Personalized Investment Recommendations**: AI-driven advice based on user profile and risk tolerance
- **Interactive Chat Interface**: Natural language conversation with AI assistant
- **Portfolio Analysis**: Comprehensive analysis of investment options and performance
- **Risk Assessment**: Intelligent risk profiling and capacity analysis
- **Retirement Projections**: Future value calculations and retirement planning
- **Educational Insights**: Financial literacy improvement through AI explanations
- **Real-time Data Processing**: Analysis of superannuation fund performance data

## 🏗️ Architecture

The application follows a hybrid approach combining:
- **RAG (Retrieval Augmented Generation)**: For knowledge-based responses
- **Machine Learning Models**: For predictive analytics and recommendations
- **Large Language Models**: For natural conversation and explanations

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker & Docker Compose (optional)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd superannuation-ai-assistant
```

2. **Place your data file**
```bash
# Copy your CSV data file to the backend/data directory
cp backend\data\problem_01.xlsx
```

3. **Start the application**
```bash
docker-compose up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up data**
```bash
# Create data directory if it doesn't exist
mkdir -p data

# Copy your CSV data file
cp backend\data\problem_01.xlsx
```

5. **Run the backend**
```bash
python app.py
```

#### Frontend Setup

1. **Open new terminal and navigate to frontend**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start the frontend**
```bash
npm start
```

## 📊 Data Setup

### CSV Data Format

Your superannuation data should be in CSV format with the following columns:

**Required Columns:**
- `Age`: User age
- `Annual_Income`: Annual income in dollars
- `Risk_Tolerance`: Low/Medium/High
- `Investment_Type`: Stocks/Bonds/ETF/Real Estate
- `Fund_Name`: Name of the investment fund
- `Annual_Return_Rate`: Expected annual return percentage
- `Volatility`: Investment volatility percentage
- `Fees_Percentage`: Management fees percentage

**Optional Columns:**
- `Current_Savings`, `Retirement_Age_Goal`, `Employment_Status`
- `Marital_Status`, `Number_of_Dependents`, `Education_Level`
- `Health_Status`, `Monthly_Expenses`, `Investment_Experience_Level`
- And other demographic/financial data points

### Sample Data

The application comes with sample data. To use your own data:

1. **Replace the sample data**
```bash
cp your_data.csv backend/data/superannuation_data.csv
```

2. **Restart the application**
```bash
# If using Docker
docker-compose restart

# If running manually
# Restart both backend and frontend servers
```

## 🔧 Configuration

### Environment Variables

Create `.env` files in both backend and frontend directories:

**Backend (.env)**
```env
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///superannuation.db
OPENAI_API_KEY=your_openai_api_key_here
MODEL_PATH=models/superannuation_model.pkl
```

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_APP_NAME=SuperAI Assistant
```

### Model Configuration

The ML model can be configured in `backend/src/ml/model.py`:

```python
# Adjust model parameters
MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42
}
```

## 📱 Usage

### 1. Complete Your Profile
- Navigate to the Profile section
- Fill in your personal and financial information
- Set your risk tolerance and retirement goals

### 2. Get Recommendations
- Visit the Recommendations section
- View personalized investment suggestions
- Explore different asset allocation strategies

### 3. Chat with AI
- Use the Chat interface for specific questions
- Ask about investment strategies, fund performance, or retirement planning
- Get educational explanations in simple terms