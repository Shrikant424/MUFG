import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'data/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple validation function
def validate_user_data(data):
    """Validate user input data based on your dataset structure"""
    if not data:
        return {'valid': False, 'message': 'User data is required'}
    
    required_fields = ['Age', 'Annual_Income', 'Risk_Tolerance']
    
    for field in required_fields:
        if field not in data:
            return {'valid': False, 'message': f'{field} is required'}
    
    # Validate age
    age = data.get('Age')
    if not isinstance(age, (int, float)) or age < 18 or age > 100:
        return {'valid': False, 'message': 'Age must be between 18 and 100'}
    
    # Validate annual income
    income = data.get('Annual_Income')
    if not isinstance(income, (int, float)) or income < 0:
        return {'valid': False, 'message': 'Annual income must be positive'}
    
    # Validate risk tolerance
    risk_tolerance = data.get('Risk_Tolerance')
    if risk_tolerance not in ['Low', 'Medium', 'High']:
        return {'valid': False, 'message': 'Risk tolerance must be Low, Medium, or High'}
    
    return {'valid': True, 'message': 'Valid data'}

# Simple recommendation service
class SimpleRecommendationService:
    def __init__(self):
        self.recommendations_cache = {}
        
    def generate_recommendations(self, user_profile):
        """Generate recommendations based on user profile"""
        age = user_profile.get('Age', 35)
        risk_tolerance = user_profile.get('Risk_Tolerance', 'Medium')
        annual_income = user_profile.get('Annual_Income', 70000)
        current_savings = user_profile.get('Current_Savings', 50000)
        
        recommendations = []
        
        # Age-based recommendations
        if age < 35:
            if risk_tolerance == 'High':
                recommendations.append({
                    'Investment_Type': 'Growth Shares',
                    'recommended_allocation': 80,
                    'expected_return': 8.5,
                    'risk_level': 'High',
                    'description': 'High growth potential with higher volatility',
                    'suitability_score': 0.9
                })
            recommendations.append({
                'Investment_Type': 'Balanced Fund',
                'recommended_allocation': 70,
                'expected_return': 7.2,
                'risk_level': 'Medium',
                'description': 'Balanced growth and defensive assets',
                'suitability_score': 0.85
            })
        elif age < 50:
            recommendations.append({
                'Investment_Type': 'Balanced Fund',
                'recommended_allocation': 60,
                'expected_return': 6.8,
                'risk_level': 'Medium',
                'description': 'Balanced approach for mid-career',
                'suitability_score': 0.9
            })
            if risk_tolerance != 'Low':
                recommendations.append({
                    'Investment_Type': 'Growth Shares',
                    'recommended_allocation': 50,
                    'expected_return': 7.8,
                    'risk_level': 'Medium-High',
                    'description': 'Growth with some defensive assets',
                    'suitability_score': 0.8
                })
        else:
            recommendations.append({
                'Investment_Type': 'Conservative Fund',
                'recommended_allocation': 50,
                'expected_return': 5.5,
                'risk_level': 'Low',
                'description': 'Capital preservation with modest growth',
                'suitability_score': 0.9
            })
            recommendations.append({
                'Investment_Type': 'Balanced Fund',
                'recommended_allocation': 40,
                'expected_return': 6.0,
                'risk_level': 'Medium-Low',
                'description': 'Defensive focus with some growth',
                'suitability_score': 0.75
            })
        
        return sorted(recommendations, key=lambda x: x['suitability_score'], reverse=True)
    
    def get_market_analysis(self):
        """Return market analysis"""
        return {
            'market_trends': {
                'australian_shares': {'performance': 'Strong', 'outlook': 'Positive'},
                'international_shares': {'performance': 'Moderate', 'outlook': 'Stable'},
                'bonds': {'performance': 'Stable', 'outlook': 'Neutral'},
                'property': {'performance': 'Growing', 'outlook': 'Positive'}
            },
            'economic_indicators': {
                'interest_rates': 'Stable',
                'inflation': 'Moderate',
                'employment': 'Strong'
            }
        }

# Simple LLM service
class SimpleLLMService:
    def process_message(self, message, user_profile, conversation_history):
        """Process chat messages"""
        age = user_profile.get('Age', 35)
        risk_tolerance = user_profile.get('Risk_Tolerance', 'Medium')
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['investment', 'invest', 'fund']):
            return f"""Based on your profile (Age: {age}, Risk: {risk_tolerance}), here are some investment insights:

For your age group, consider:
- {"Growth-focused investments" if age < 40 else "Balanced to conservative approach"}
- Diversification across asset classes
- Regular contribution reviews
- Fee minimization strategies

Your {risk_tolerance.lower()} risk tolerance suggests {"you can handle more volatility for higher returns" if risk_tolerance == "High" else "a balanced approach between growth and stability" if risk_tolerance == "Medium" else "focusing on capital preservation"}

Would you like specific fund recommendations or help with contribution strategies?"""

        elif any(word in message_lower for word in ['risk', 'safe', 'conservative']):
            return f"""Understanding risk in superannuation:

Your current risk tolerance: {risk_tolerance}

Risk considerations for age {age}:
- Time horizon: {65-age} years to traditional retirement
- Risk capacity: {"Higher" if age < 45 else "Moderate" if age < 60 else "Lower"}
- Volatility tolerance: Match investments to comfort level

Key principle: Don't take more risk than you can sleep with, but don't be so conservative that inflation erodes your purchasing power.

Would you like help assessing if your current risk level is appropriate?"""

        else:
            return f"""Hello! I'm your superannuation AI assistant. 

Based on your profile:
- Age: {age}
- Risk Tolerance: {risk_tolerance}

I can help you with:
• Investment strategy recommendations
• Risk assessment and portfolio allocation  
• Retirement planning calculations
• Fee analysis and optimization
• Contribution strategies
• Market insights and education

What specific aspect of your superannuation would you like to explore?"""
    
    def get_educational_content(self, topic, level):
        """Get educational content"""
        content_map = {
            'superannuation_basics': {
                'title': 'Superannuation Fundamentals',
                'content': 'Superannuation is your retirement savings, built through employer contributions (currently 11%) and optional personal contributions.',
                'tips': ['Check your balance regularly', 'Consolidate accounts', 'Review investment options']
            },
            'investment_types': {
                'title': 'Investment Options',
                'content': 'Super funds typically offer cash, bonds, property, Australian shares, and international shares.',
                'tips': ['Diversify across asset classes', 'Consider your time horizon', 'Review fees']
            }
        }
        
        return content_map.get(topic, {
            'title': 'General Information',
            'content': 'Educational content for this topic is being developed.',
            'tips': ['Consult with a financial advisor', 'Research thoroughly']
        })

# Simple prediction model
class SimplePredictionModel:
    def predict_future_value(self, user_profile, investment_allocation):
        """Simple future value prediction"""
        current_age = user_profile.get('Age', 35)
        retirement_age = user_profile.get('Retirement_Age_Goal', 65)
        current_savings = user_profile.get('Current_Savings', 50000)
        annual_income = user_profile.get('Annual_Income', 70000)
        
        years_to_retirement = max(retirement_age - current_age, 1)
        annual_contribution = annual_income * 0.11  # Employer contribution
        
        # Simple compound interest calculation
        expected_return = 0.07  # 7% default
        
        # Calculate future value
        fv_current = current_savings * ((1 + expected_return) ** years_to_retirement)
        fv_contributions = annual_contribution * (((1 + expected_return) ** years_to_retirement - 1) / expected_return)
        
        total_projected = fv_current + fv_contributions
        
        return {
            'projected_balance': round(total_projected, 0),
            'annual_income_at_4_percent': round(total_projected * 0.04, 0),
            'years_to_retirement': years_to_retirement,
            'total_contributions': round(annual_contribution * years_to_retirement, 0),
            'growth_from_returns': round((fv_current - current_savings) + (fv_contributions - annual_contribution * years_to_retirement), 0)
        }
    
    def train(self, data):
        """Mock training function"""
        logger.info(f"Training with {len(data)} records")
        pass

# Initialize services
recommendation_service = SimpleRecommendationService()
llm_service = SimpleLLMService()
predictor = SimplePredictionModel()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat interactions"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_profile = data.get('user_profile', {})
        conversation_history = data.get('conversation_history', [])
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        response = llm_service.process_message(user_message, user_profile, conversation_history)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/profile', methods=['POST'])
def create_profile():
    """Create user profile"""
    try:
        data = request.get_json()
        
        validation_result = validate_user_data(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # Map to your dataset structure
        user_profile = {
            'Age': data.get('Age'),
            'Annual_Income': data.get('Annual_Income'),
            'Current_Savings': data.get('Current_Savings', 0),
            'Retirement_Age_Goal': data.get('Retirement_Age_Goal', 65),
            'Risk_Tolerance': data.get('Risk_Tolerance'),
            'Employment_Status': data.get('Employment_Status', 'Full-time'),
            'Marital_Status': data.get('Marital_Status', 'Single'),
            'Number_of_Dependents': data.get('Number_of_Dependents', 0),
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'message': 'Profile created successfully',
            'profile': user_profile
        })
        
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get recommendations"""
    try:
        data = request.get_json()
        print(f"Received request data: {data}")  # Debug logging
        
        user_profile = data.get('user_profile', {})
        print(f"User profile: {user_profile}")  # Debug logging
        
        if not user_profile:
            return jsonify({'error': 'User profile required'}), 400
        
        # Validate required fields
        required_fields = ['Age', 'Annual_Income', 'Risk_Tolerance']
        missing_fields = [field for field in required_fields if field not in user_profile]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        recommendations = recommendation_service.generate_recommendations(user_profile)
        print(f"Generated recommendations: {recommendations}")  # Debug logging
        
        return jsonify({
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        print(f"Exception in get_recommendations: {str(e)}")  # Debug logging
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
@app.route('/api/predict', methods=['POST'])
def predict_returns():
    """Predict future returns"""
    try:
        data = request.get_json()
        user_profile = data.get('user_profile', {})
        investment_allocation = data.get('investment_allocation', {})
        
        predictions = predictor.predict_future_value(user_profile, investment_allocation)
        
        return jsonify({
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/risk-assessment', methods=['POST'])
def risk_assessment():
    """Risk assessment endpoint"""
    try:
        user_data = request.json
        age = user_data.get('Age', 35)
        risk_tolerance = user_data.get('Risk_Tolerance', 'Medium')
        
        assessment = {
            'risk_profile': risk_tolerance,
            'age_factor': 'Conservative' if age > 55 else 'Moderate' if age > 40 else 'Aggressive',
            'recommendation': f'Based on age {age} and {risk_tolerance} tolerance, consider a balanced approach.'
        }
        
        return jsonify(assessment)
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/market-analysis', methods=['GET'])
def market_analysis():
    """Market analysis"""
    try:
        analysis = recommendation_service.get_market_analysis()
        return jsonify({
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting market analysis: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/education', methods=['GET'])
def get_educational_content():
    """Educational content"""
    try:
        topic = request.args.get('topic', 'general')
        level = request.args.get('level', 'beginner')
        
        content = llm_service.get_educational_content(topic, level)
        
        return jsonify({
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting educational content: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Try to load dataset
    try:
        df = pd.read_excel("data/problem_01.xlsx")
        predictor.train(df)
        logger.info("Model trained successfully")
    except Exception as e:
        logger.warning(f"Could not load dataset: {str(e)}")
        logger.info("Running with mock data")
    
    app.run(debug=True, host='0.0.0.0', port=5000)