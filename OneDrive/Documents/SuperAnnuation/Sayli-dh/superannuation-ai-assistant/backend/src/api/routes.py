from flask import Blueprint, request, jsonify
from src.services.llm_service import LLMService
from src.services.recommendation_service import RecommendationService
from src.ml.model import SuperannuationPredictor
from src.utils.helpers import validate_user_data, format_response
import logging

api_bp = Blueprint('api', __name__)

# Initialize services
llm_service = LLMService()
recommendation_service = RecommendationService()
investment_model = SuperannuationPredictor()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@api_bp.route('/user/profile', methods=['POST'])
def save_user_profile():
    """Save or update user profile"""
    try:
        user_data = request.json
        
        # Validate user data
        if not validate_user_data(user_data):
            return jsonify({'error': 'Invalid user data'}), 400
        
        # Here you would typically save to database
        # For now, we'll just return success
        
        return jsonify({
            'message': 'Profile saved successfully',
            'data': user_data
        })
    except Exception as e:
        logging.error(f"Error saving user profile: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Get investment recommendations based on user profile"""
    try:
        user_data = request.json
        
        # Get ML-based recommendations
        recommendations = recommendation_service.get_recommendations(user_data)
        
        return jsonify({
            'recommendations': recommendations,
            'message': 'Recommendations generated successfully'
        })
    except Exception as e:
        logging.error(f"Error getting recommendations: {e}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat interactions"""
    try:
        data = request.json
        message = data.get('message', '')
        user_context = data.get('userContext', {})
        
        # Process message through LLM
        response = llm_service.process_message(message, user_context)
        
        return jsonify({
            'response': response,
            'timestamp': data.get('timestamp')
        })
    except Exception as e:
        logging.error(f"Error processing chat message: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

@api_bp.route('/analyze', methods=['POST'])
def analyze_portfolio():
    """Analyze user's current portfolio"""
    try:
        portfolio_data = request.json
        
        # Perform portfolio analysis
        analysis = investment_model.analyze_portfolio(portfolio_data)
        
        return jsonify({
            'analysis': analysis,
            'message': 'Portfolio analysis completed'
        })
    except Exception as e:
        logging.error(f"Error analyzing portfolio: {e}")
        return jsonify({'error': 'Failed to analyze portfolio'}), 500

@api_bp.route('/market-data', methods=['GET'])
def get_market_data():
    """Get current market data and trends"""
    try:
        market_data = recommendation_service.get_market_trends()
        
        return jsonify({
            'marketData': market_data,
            'timestamp': pd.Timestamp.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error fetching market data: {e}")
        return jsonify({'error': 'Failed to fetch market data'}), 500

@api_bp.route('/risk-assessment', methods=['POST'])
def assess_risk():
    """Assess user's risk profile"""
    try:
        user_data = request.json
        
        risk_assessment = investment_model.assess_risk_profile(user_data)
        
        return jsonify({
            'riskAssessment': risk_assessment,
            'message': 'Risk assessment completed'
        })
    except Exception as e:
        logging.error(f"Error assessing risk: {e}")
        return jsonify({'error': 'Failed to assess risk'}), 500