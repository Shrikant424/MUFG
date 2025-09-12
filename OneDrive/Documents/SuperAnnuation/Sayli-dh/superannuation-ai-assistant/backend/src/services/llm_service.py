import openai
import os
from typing import Dict, List, Any
import json
from datetime import datetime
import logging
from config import EDUCATIONAL_TOPICS

logger = logging.getLogger(__name__)

class LLMService:
    """Service for handling Large Language Model interactions"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # System prompt for the superannuation assistant
        self.system_prompt = """
        You are an expert Australian superannuation and investment advisor AI assistant. 
        Your role is to help users make informed decisions about their superannuation investments.
        
        Key principles:
        1. Always provide personalized advice based on user's profile (age, income, risk tolerance, goals)
        2. Explain complex financial concepts in simple terms
        3. Consider Australian superannuation rules and tax implications
        4. Emphasize the importance of diversification and long-term investing
        5. Be transparent about risks and potential returns
        6. Never guarantee specific returns - always discuss estimates and ranges
        7. Encourage users to consider their complete financial situation
        8. Provide educational insights to improve financial literacy
        
        When discussing investments, always mention:
        - Risk level and time horizon suitability
        - Expected returns (as estimates/ranges)
        - Fees and their impact over time
        - Diversification benefits
        - Tax considerations
        
        Keep responses conversational but informative. Use examples when helpful.
        """
    
    def process_message(self, user_message: str, user_profile: Dict, conversation_history: List[Dict]) -> str:
        """Process user message and generate AI response"""
        try:
            # Build context from user profile
            context = self._build_context(user_profile)
            
            # Format conversation history
            messages = [{"role": "system", "content": self.system_prompt + "\n\n" + context}]
            
            # Add conversation history
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Check if OpenAI API is available
            if not self.api_key:
                return self._fallback_response(user_message, user_profile)
            
            # Generate response using OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in LLM service: {str(e)}")
            return self._fallback_response(user_message, user_profile)
    
    def _build_context(self, user_profile: Dict) -> str:
        """Build context string from user profile"""
        if not user_profile:
            return "User profile not available."
        
        context_parts = []
        context_parts.append("Current user profile:")
        
        if 'age' in user_profile:
            context_parts.append(f"- Age: {user_profile['age']}")
            years_to_retirement = user_profile.get('retirement_age_goal', 65) - user_profile['age']
            context_parts.append(f"- Years until retirement: {max(0, years_to_retirement)}")
        
        if 'annual_income' in user_profile:
            context_parts.append(f"- Annual income: ${user_profile['annual_income']:,}")
        
        if 'current_savings' in user_profile:
            context_parts.append(f"- Current superannuation balance: ${user_profile['current_savings']:,}")
        
        if 'risk_tolerance' in user_profile:
            context_parts.append(f"- Risk tolerance: {user_profile['risk_tolerance']}")
        
        if 'employment_status' in user_profile:
            context_parts.append(f"- Employment status: {user_profile['employment_status']}")
        
        if 'financial_goals' in user_profile:
            goals = ', '.join(user_profile['financial_goals'])
            context_parts.append(f"- Financial goals: {goals}")
        
        return '\n'.join(context_parts)
    
    def _fallback_response(self, user_message: str, user_profile: Dict) -> str:
        """Provide fallback response when OpenAI is not available"""
        # Simple rule-based responses for common queries
        message_lower = user_message.lower()
        
        age = user_profile.get('age', 35)
        risk_tolerance = user_profile.get('risk_tolerance', 'Medium')
        
        if any(word in message_lower for word in ['investment', 'invest', 'portfolio']):
            if age < 35 and risk_tolerance == 'High':
                return """Based on your young age and high risk tolerance, you might consider:

• **Growth/High Growth options** (70-80% growth assets)
• **Index funds or ETFs** for low fees and diversification  
• **International shares** for global diversification
• **Property/REIT exposure** for inflation protection

Remember, you have time to ride out market volatility. Focus on low fees and diversification. Consider reviewing your strategy every 3-5 years as your circumstances change.

Would you like me to explain any of these investment types in more detail?"""
            
            elif age > 50:
                return """As you're closer to retirement, consider:

• **Balanced to Conservative options** (40-60% growth assets)
• **Gradual shift to more defensive assets** over time
• **Consider your total retirement income needs**
• **Review insurance within super**

The key is maintaining some growth exposure while reducing volatility as you approach retirement. 

Would you like to discuss retirement income planning strategies?"""
        
        if any(word in message_lower for word in ['risk', 'safe', 'conservative']):
            return """Understanding investment risk is crucial:

• **Conservative**: Lower volatility, lower expected returns (3-5% p.a.)
• **Balanced**: Moderate risk/return (5-7% p.a.)  
• **Growth**: Higher volatility, higher potential returns (6-9% p.a.)

Your risk tolerance should consider:
- Time until retirement
- Comfort with market fluctuations
- Other income sources in retirement
- Personal circumstances

Remember: staying too conservative can be risky too - inflation erodes purchasing power over time.

What's your biggest concern about investment risk?"""
        
        if any(word in message_lower for word in ['fee', 'fees', 'cost']):
            return """Investment fees significantly impact long-term returns:

• **Administration fees**: 0.1-0.8% annually
• **Investment management fees**: 0.05-2.0% depending on option
• **Insurance premiums**: If held within super

**Example**: 1% in extra fees on $100,000 costs ~$25,000 over 25 years!

Look for:
- Total fee percentages
- Index options (typically 0.05-0.15% fees)
- Fee comparison tools from your super fund

Would you like help calculating how fees might impact your specific situation?"""
        
        return """I'm here to help with your superannuation and investment questions! I can assist with:

• Investment strategy and asset allocation
• Understanding different super investment options  
• Risk assessment and time horizon planning
• Fee analysis and cost optimization
• Retirement income planning
• Tax considerations for super

What specific aspect of superannuation would you like to explore? Feel free to ask about your situation - the more details you share, the more personalized advice I can provide."""
    
    def get_educational_content(self, topic: str, user_level: str = 'beginner') -> Dict[str, Any]:
        """Generate educational content on financial topics"""
        
        educational_content = {
            'superannuation_basics': {
                'beginner': {
                    'title': 'Superannuation Basics',
                    'content': """
                    **What is Superannuation?**
                    
                    Superannuation (super) is money set aside during your working life for your retirement. In Australia, it's mandatory - your employer must contribute at least 11% of your salary to your super fund.
                    
                    **Key Benefits:**
                    • Tax advantages during accumulation and retirement
                    • Compound growth over decades
                    • Professional investment management
                    • Insurance options
                    
                    **How it works:**
                    1. Employer contributes 11% of your salary
                    2. You can make additional contributions
                    3. Money is invested in various assets
                    4. Balance grows over time through returns and contributions
                    5. Access funds after age 65 (or preservation age)
                    
                    The earlier you start optimizing your super, the more time compound interest has to work for you!
                    """,
                    'tips': [
                        'Check your super balance regularly',
                        'Consolidate multiple super accounts',
                        'Consider making extra contributions',
                        'Review your investment options annually'
                    ]
                }
            },
            'investment_types': {
                'beginner': {
                    'title': 'Types of Super Investments',
                    'content': """
                    **Main Asset Classes in Super:**
                    
                    **🏦 Cash & Fixed Interest (Defensive)**
                    • Bank deposits, government bonds
                    • Lower risk, lower returns (2-4% p.a.)
                    • Provides stability and regular income
                    
                    **📈 Australian Shares (Growth)**
                    • Ownership in Australian companies
                    • Higher risk/return potential (6-10% p.a. long-term)
                    • Provides capital growth and dividends
                    
                    **🌍 International Shares (Growth)**
                    • Global company ownership
                    • Currency risk but diversification benefits
                    • Access to different economies and sectors
                    
                    **🏘️ Property/REITs (Growth)**
                    • Real estate investment trusts
                    • Inflation protection
                    • Rental income plus capital growth
                    
                    **💡 Most super funds offer:**
                    • Pre-mixed options (Conservative, Balanced, Growth)
                    • Choice of individual asset classes
                    • Lifecycle options that adjust with age
                    """
                }
            },
            'risk_management': {
                'beginner': {
                    'title': 'Understanding Investment Risk',
                    'content': """
                    **Types of Investment Risk:**
                    
                    **📊 Market Risk**
                    • Share prices go up and down
                    • Short-term volatility is normal
                    • Time diversification helps (longer = less risky)
                    
                    **💰 Inflation Risk**
                    • Money loses purchasing power over time
                    • Cash may not keep up with inflation
                    • Growth assets help combat inflation
                    
                    **🏢 Company Risk**
                    • Individual companies can fail
                    • Diversification across many companies reduces this
                    • Index funds spread risk automatically
                    
                    **🌏 Currency Risk**
                    • International investments affected by exchange rates
                    • Can work for or against you
                    • Hedged vs unhedged options available
                    
                    **⚖️ Risk vs Time Horizon:**
                    • 20+ years to retirement: Can take more risk
                    • 10 years to retirement: Moderate risk
                    • <5 years to retirement: Lower risk focus
                    
                    Remember: Not taking enough risk can also be risky!
                    """
                }
            }
        }
        
        content = educational_content.get(topic, {}).get(user_level, {})
        if not content:
            content = {
                'title': f'Information about {topic.replace("_", " ").title()}',
                'content': 'Educational content coming soon for this topic.',
                'tips': ['Check back later for more detailed information']
            }
        
        return {
            'topic': topic,
            'level': user_level,
            'title': content.get('title', ''),
            'content': content.get('content', ''),
            'tips': content.get('tips', []),
            'generated_at': datetime.now().isoformat()
        }