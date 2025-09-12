import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

def validate_user_data(user_data):
    """Validate user input data"""
    required_fields = ['age', 'annualIncome', 'riskTolerance']
    
    # Check required fields
    for field in required_fields:
        if field not in user_data:
            return False
    
    # Validate age
    age = user_data.get('age')
    if not isinstance(age, (int, float)) or age < 18 or age > 100:
        return False
    
    # Validate annual income
    income = user_data.get('annualIncome')
    if not isinstance(income, (int, float)) or income < 0:
        return False
    
    # Validate risk tolerance
    risk_tolerance = user_data.get('riskTolerance')
    if risk_tolerance not in ['Low', 'Medium', 'High']:
        return False
    
    return True

def format_response(data, message="Success"):
    """Format API response"""
    return {
        'status': 'success',
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }

def calculate_compound_interest(principal, rate, time, contributions=0, contribution_frequency=1):
    """Calculate compound interest with regular contributions"""
    # Convert annual rate to decimal
    r = rate / 100
    
    # Future value of principal
    fv_principal = principal * (1 + r) ** time
    
    # Future value of annuity (regular contributions)
    if contributions > 0:
        fv_contributions = contributions * contribution_frequency * (
            ((1 + r) ** time - 1) / r
        )
    else:
        fv_contributions = 0
    
    return fv_principal + fv_contributions

def calculate_retirement_needs(current_age, retirement_age, current_expenses, inflation_rate=0.03):
    """Calculate estimated retirement needs"""
    years_to_retirement = retirement_age - current_age
    
    # Adjust expenses for inflation
    future_expenses = current_expenses * (1 + inflation_rate) ** years_to_retirement
    
    # Assume 25x annual expenses needed (4% withdrawal rule)
    retirement_corpus_needed = future_expenses * 25
    
    return {
        'years_to_retirement': years_to_retirement,
        'future_annual_expenses': round(future_expenses, 2),
        'retirement_corpus_needed': round(retirement_corpus_needed, 2)
    }

def assess_risk_capacity(user_profile):
    """Assess user's risk capacity based on profile"""
    score = 0
    
    # Age factor (younger = higher risk capacity)
    age = user_profile.get('age', 35)
    if age < 30:
        score += 0.3
    elif age < 40:
        score += 0.25
    elif age < 50:
        score += 0.2
    elif age < 60:
        score += 0.1
    
    # Income factor
    income = user_profile.get('annualIncome', 70000)
    if income > 150000:
        score += 0.3
    elif income > 100000:
        score += 0.25
    elif income > 70000:
        score += 0.2
    elif income > 50000:
        score += 0.15
    else:
        score += 0.1
    
    # Savings factor
    savings = user_profile.get('currentSavings', 100000)
    if savings > 500000:
        score += 0.2
    elif savings > 200000:
        score += 0.15
    elif savings > 100000:
        score += 0.1
    elif savings > 50000:
        score += 0.05
    
    # Time horizon factor
    years_to_retirement = user_profile.get('yearsToRetirement', 30)
    if years_to_retirement > 30:
        score += 0.2
    elif years_to_retirement > 20:
        score += 0.15
    elif years_to_retirement > 10:
        score += 0.1
    else:
        score += 0.05
    
    # Normalize score to 0-1 range
    normalized_score = min(score, 1.0)
    
    # Convert to risk category
    if normalized_score > 0.7:
        return 'High'
    elif normalized_score > 0.4:
        return 'Medium'
    else:
        return 'Low'

def calculate_portfolio_metrics(portfolio_data):
    """Calculate portfolio performance metrics"""
    if not portfolio_data or 'holdings' not in portfolio_data:
        return {}
    
    holdings = portfolio_data['holdings']
    total_value = sum(holding.get('value', 0) for holding in holdings)
    
    if total_value == 0:
        return {}
    
    # Calculate weighted average return
    weighted_return = sum(
        holding.get('value', 0) * holding.get('return', 0) / total_value
        for holding in holdings
    )
    
    # Calculate portfolio volatility (simplified)
    weighted_volatility = sum(
        holding.get('value', 0) * holding.get('volatility', 0) / total_value
        for holding in holdings
    )
    
    # Calculate Sharpe ratio (simplified, assuming risk-free rate of 2%)
    risk_free_rate = 2.0
    sharpe_ratio = (weighted_return - risk_free_rate) / weighted_volatility if weighted_volatility > 0 else 0
    
    # Diversification score (based on number of different asset types)
    asset_types = set(holding.get('type', 'Unknown') for holding in holdings)
    diversification_score = min(len(asset_types) / 5, 1.0)  # Max score at 5+ asset types
    
    return {
        'total_value': round(total_value, 2),
        'weighted_return': round(weighted_return, 2),
        'volatility': round(weighted_volatility, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'diversification_score': round(diversification_score, 2),
        'asset_allocation': get_asset_allocation(holdings)
    }

def get_asset_allocation(holdings):
    """Calculate asset allocation percentages"""
    total_value = sum(holding.get('value', 0) for holding in holdings)
    
    if total_value == 0:
        return {}
    
    allocation = {}
    for holding in holdings:
        asset_type = holding.get('type', 'Unknown')
        value = holding.get('value', 0)
        percentage = (value / total_value) * 100
        
        if asset_type in allocation:
            allocation[asset_type] += percentage
        else:
            allocation[asset_type] = percentage
    
    # Round percentages
    allocation = {k: round(v, 1) for k, v in allocation.items()}
    
    return allocation

def generate_portfolio_insights(portfolio_metrics, user_profile):
    """Generate insights about the portfolio"""
    insights = []
    
    # Return insight
    current_return = portfolio_metrics.get('weighted_return', 0)
    if current_return > 8:
        insights.append(f"Your portfolio is performing well with {current_return}% returns.")
    elif current_return > 5:
        insights.append(f"Your portfolio shows moderate performance at {current_return}% returns.")
    else:
        insights.append(f"Your portfolio returns of {current_return}% could be improved.")
    
    # Risk insight
    volatility = portfolio_metrics.get('volatility', 0)
    risk_tolerance = user_profile.get('riskTolerance', 'Medium')
    
    if risk_tolerance == 'Low' and volatility > 4:
        insights.append("Your portfolio volatility seems high for your risk tolerance.")
    elif risk_tolerance == 'High' and volatility < 2:
        insights.append("You might consider more growth-oriented investments given your risk tolerance.")
    
    # Diversification insight
    diversification_score = portfolio_metrics.get('diversification_score', 0)
    if diversification_score < 0.5:
        insights.append("Consider diversifying across more asset classes to reduce risk.")
    
    return insights

def format_currency(amount, currency='AUD'):
    """Format currency values"""
    if amount >= 1000000:
        return f"${amount/1000000:.1f}M {currency}"
    elif amount >= 1000:
        return f"${amount/1000:.0f}K {currency}"
    else:
        return f"${amount:.0f} {currency}"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(input_string):
    """Sanitize user input to prevent XSS"""
    if not isinstance(input_string, str):
        return input_string
    
    # Remove potential HTML tags
    clean_string = re.sub(r'<[^>]+>', '', input_string)
    
    # Remove potential script tags
    clean_string = re.sub(r'<script.*?</script>', '', clean_string, flags=re.DOTALL | re.IGNORECASE)
    
    return clean_string.strip()

def calculate_time_to_goal(current_value, target_value, monthly_contribution, annual_return):
    """Calculate time needed to reach financial goal"""
    if target_value <= current_value:
        return 0
    
    if monthly_contribution <= 0:
        return float('inf')
    
    monthly_rate = annual_return / 12 / 100
    
    if monthly_rate == 0:
        # Simple calculation without compound interest
        remaining_amount = target_value - current_value
        months_needed = remaining_amount / monthly_contribution
    else:
        # Calculate with compound interest
        # Formula: FV = PV(1+r)^n + PMT[((1+r)^n - 1)/r]
        # Solve for n (number of periods)
        try:
            fv_pv_ratio = target_value / current_value if current_value > 0 else float('inf')
            pmt_contribution = monthly_contribution / current_value if current_value > 0 else 0
            
            # Numerical approximation for time to goal
            months_needed = 0
            current_val = current_value
            
            while current_val < target_value and months_needed < 600:  # Max 50 years
                current_val = current_val * (1 + monthly_rate) + monthly_contribution
                months_needed += 1
                
        except:
            months_needed = float('inf')
    
    return round(months_needed / 12, 1)  # Return years

def calculate_optimal_contribution(current_value, target_value, years_available, annual_return):
    """Calculate optimal monthly contribution to reach goal"""
    if years_available <= 0:
        return float('inf')
    
    months = years_available * 12
    monthly_rate = annual_return / 12 / 100
    
    if monthly_rate == 0:
        # Simple calculation without compound interest
        future_value_current = current_value
        remaining_needed = target_value - future_value_current
        monthly_contribution = remaining_needed / months
    else:
        # Calculate required monthly contribution with compound interest
        future_value_current = current_value * (1 + monthly_rate) ** months
        remaining_needed = target_value - future_value_current
        
        if remaining_needed <= 0:
            return 0
        
        # PMT calculation
        monthly_contribution = remaining_needed * monthly_rate / ((1 + monthly_rate) ** months - 1)
    
    return max(0, round(monthly_contribution, 2))

def analyze_fund_performance(fund_data, benchmark_return=7.0):
    """Analyze investment fund performance"""
    if not fund_data:
        return {}
    
    annual_return = fund_data.get('annual_return', 0)
    volatility = fund_data.get('volatility', 0)
    fees = fund_data.get('fees_percentage', 0)
    
    # Performance metrics
    excess_return = annual_return - benchmark_return
    risk_adjusted_return = (annual_return - 2.0) / volatility if volatility > 0 else 0  # Sharpe ratio
    net_return = annual_return - fees
    
    # Performance rating
    if net_return >= 10:
        rating = 'Excellent'
    elif net_return >= 8:
        rating = 'Good'
    elif net_return >= 6:
        rating = 'Fair'
    else:
        rating = 'Poor'
    
    return {
        'fund_name': fund_data.get('fund_name', 'Unknown'),
        'annual_return': annual_return,
        'volatility': volatility,
        'fees': fees,
        'net_return': round(net_return, 2),
        'excess_return': round(excess_return, 2),
        'sharpe_ratio': round(risk_adjusted_return, 2),
        'rating': rating
    }

def get_asset_allocation_recommendation(risk_tolerance, age):
    """Get recommended asset allocation based on risk tolerance and age"""
    base_stock_allocation = max(100 - age, 20)  # Age-based rule of thumb
    
    if risk_tolerance == 'High':
        stocks = min(base_stock_allocation + 20, 90)
    elif risk_tolerance == 'Medium':
        stocks = base_stock_allocation
    else:  # Low risk
        stocks = max(base_stock_allocation - 20, 10)
    
    bonds = max(100 - stocks - 10, 10)
    alternatives = 100 - stocks - bonds
    
    return {
        'stocks': stocks,
        'bonds': bonds,
        'alternatives': alternatives
    }

def calculate_retirement_income_replacement(current_income, target_replacement_ratio=0.8):
    """Calculate required retirement income"""
    return current_income * target_replacement_ratio

def estimate_life_expectancy(age, gender, health_status='Average'):
    """Estimate life expectancy for retirement planning"""
    base_life_expectancy = {
        'Male': 84,
        'Female': 87,
        'Other': 85
    }
    
    base = base_life_expectancy.get(gender, 85)
    
    # Adjust for health status
    if health_status == 'Excellent':
        adjustment = 5
    elif health_status == 'Good':
        adjustment = 2
    elif health_status == 'Average':
        adjustment = 0
    elif health_status == 'Poor':
        adjustment = -3
    else:
        adjustment = 0
    
    return min(base + adjustment, 100)

def calculate_pension_sustainability(annual_withdrawal, portfolio_value, inflation_rate=0.03):
    """Calculate how long pension will last"""
    if annual_withdrawal <= 0:
        return float('inf')
    
    # Simple calculation assuming no investment growth
    years_sustainable = portfolio_value / annual_withdrawal
    
    # Adjust for inflation impact
    real_years = years_sustainable * (1 - inflation_rate)
    
    return max(0, round(real_years, 1))

def generate_investment_mix_recommendation(user_profile):
    """Generate specific investment mix recommendation"""
    age = user_profile.get('age', 35)
    risk_tolerance = user_profile.get('riskTolerance', 'Medium')
    years_to_retirement = user_profile.get('yearsToRetirement', 30)
    
    allocation = get_asset_allocation_recommendation(risk_tolerance, age)
    
    # Specific investment recommendations
    recommendations = {
        'allocation': allocation,
        'specific_funds': []
    }
    
    # Add specific fund types based on allocation
    if allocation['stocks'] > 50:
        recommendations['specific_funds'].extend([
            'Australian Shares ETF',
            'International Shares ETF',
            'Growth-oriented Managed Fund'
        ])
    
    if allocation['bonds'] > 20:
        recommendations['specific_funds'].extend([
            'Government Bonds',
            'Corporate Bonds',
            'Fixed Income Fund'
        ])
    
    if allocation['alternatives'] > 0:
        recommendations['specific_funds'].extend([
            'Property Investment Trust',
            'Infrastructure Fund'
        ])
    
    return recommendations