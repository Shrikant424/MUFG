import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.ml.model import SuperannuationPredictor 
import joblib
import os

class RecommendationService:
    def __init__(self):
        self.model = SuperannuationPredictor()
        self.scaler = StandardScaler()
        self.data_path = os.path.join("backend", "data", "problem_01.xlsx")
        self.load_data()
    
    def load_data(self):
        """Load and preprocess the superannuation data"""
        try:
            if os.path.exists(self.data_path):
                self.df = pd.read_csv(self.data_path)
                self.preprocess_data()
            else:
                print(f"Data file not found at {self.data_path}")
                self.df = None
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = None
    
    def preprocess_data(self):
        """Preprocess the data for recommendations"""
        # Convert categorical variables
        categorical_columns = ['Gender', 'Country', 'Employment_Status', 'Risk_Tolerance', 
                             'Investment_Type', 'Marital_Status', 'Education_Level', 
                             'Health_Status', 'Home_Ownership_Status']
        
        for col in categorical_columns:
            if col in self.df.columns:
                self.df[col + '_encoded'] = pd.Categorical(self.df[col]).codes
        
        # Fill missing values
        self.df = self.df.fillna(self.df.mean(numeric_only=True))
    
    def get_recommendations(self, user_profile):
        """Generate personalized investment recommendations"""
        try:
            if self.df is None:
                return self._get_default_recommendations()
            
            # Find similar users
            similar_users = self._find_similar_users(user_profile)
            
            # Generate recommendations based on similar users
            recommendations = self._generate_recommendations(user_profile, similar_users)
            
            return recommendations
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self._get_default_recommendations()
    
    def _find_similar_users(self, user_profile, top_n=10):
        """Find users with similar profiles using cosine similarity"""
        # Create user vector
        user_vector = self._create_user_vector(user_profile)
        
        # Create comparison vectors from existing data
        feature_columns = ['Age', 'Annual_Income', 'Current_Savings', 'Retirement_Age_Goal',
                          'Risk_Tolerance_encoded', 'Years_Contributed', 'Investment_Experience_Level']
        
        existing_vectors = self.df[feature_columns].values
        user_vector_reshaped = user_vector.reshape(1, -1)
        
        # Calculate similarity
        similarities = cosine_similarity(user_vector_reshaped, existing_vectors)[0]
        
        # Get top similar users
        similar_indices = np.argsort(similarities)[-top_n:]
        return self.df.iloc[similar_indices]
    
    def _create_user_vector(self, user_profile):
        """Create numerical vector from user profile"""
        risk_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
        experience_mapping = {'Beginner': 0, 'Intermediate': 1, 'Expert': 2}
        
        vector = np.array([
            user_profile.get('age', 35),
            user_profile.get('annualIncome', 70000),
            user_profile.get('currentSavings', 100000),
            user_profile.get('retirementAge', 65),
            risk_mapping.get(user_profile.get('riskTolerance', 'Medium'), 1),
            user_profile.get('yearsToRetirement', 30),
            experience_mapping.get(user_profile.get('investmentExperience', 'Intermediate'), 1)
        ])
        
        return vector
    
    def _generate_recommendations(self, user_profile, similar_users):
        """Generate investment recommendations based on similar users"""
        recommendations = []
        
        # Analyze popular investment types among similar users
        investment_popularity = similar_users['Investment_Type'].value_counts()
        
        # Calculate average returns for each investment type
        avg_returns = similar_users.groupby('Investment_Type')['Annual_Return_Rate'].mean()
        
        # Generate top 3 recommendations
        for investment_type in investment_popularity.head(3).index:
            similar_investments = similar_users[similar_users['Investment_Type'] == investment_type]
            
            recommendation = {
                'investmentType': investment_type,
                'averageReturn': round(avg_returns[investment_type], 2),
                'riskLevel': self._get_risk_level(similar_investments),
                'projectedValue': self._calculate_projected_value(user_profile, avg_returns[investment_type]),
                'fees': round(similar_investments['Fees_Percentage'].mean(), 2),
                'volatility': round(similar_investments['Volatility'].mean(), 2),
                'suitabilityScore': self._calculate_suitability_score(user_profile, similar_investments),
                'explanation': self._generate_explanation(investment_type, user_profile),
                'funds': self._get_top_funds(investment_type, similar_investments)
            }
            
            recommendations.append(recommendation)
        
        return sorted(recommendations, key=lambda x: x['suitabilityScore'], reverse=True)
    
    def _get_risk_level(self, investments):
        """Determine risk level based on volatility"""
        avg_volatility = investments['Volatility'].mean()
        if avg_volatility < 2:
            return 'Low'
        elif avg_volatility < 4:
            return 'Medium'
        else:
            return 'High'
    
    def _calculate_projected_value(self, user_profile, annual_return):
        """Calculate projected retirement value"""
        current_savings = user_profile.get('currentSavings', 100000)
        annual_contribution = user_profile.get('annualContribution', 10000)
        years_to_retirement = user_profile.get('yearsToRetirement', 30)
        
        # Simple compound interest calculation
        future_value_savings = current_savings * ((1 + annual_return/100) ** years_to_retirement)
        future_value_contributions = annual_contribution * (((1 + annual_return/100) ** years_to_retirement - 1) / (annual_return/100))
        
        return round(future_value_savings + future_value_contributions, 0)
    
    def _calculate_suitability_score(self, user_profile, investments):
        """Calculate how suitable this investment is for the user"""
        score = 0
        
        # Risk alignment
        user_risk = user_profile.get('riskTolerance', 'Medium')
        investment_risk = self._get_risk_level(investments)
        
        if user_risk == investment_risk:
            score += 0.4
        elif abs(['Low', 'Medium', 'High'].index(user_risk) - ['Low', 'Medium', 'High'].index(investment_risk)) == 1:
            score += 0.2
        
        # Return potential
        avg_return = investments['Annual_Return_Rate'].mean()
        if avg_return > 7:
            score += 0.3
        elif avg_return > 5:
            score += 0.2
        elif avg_return > 3:
            score += 0.1
        
        # Low fees bonus
        avg_fees = investments['Fees_Percentage'].mean()
        if avg_fees < 1:
            score += 0.2
        elif avg_fees < 1.5:
            score += 0.1
        
        # Experience alignment
        user_experience = user_profile.get('investmentExperience', 'Intermediate')
        if investment_risk == 'Low' and user_experience == 'Beginner':
            score += 0.1
        elif investment_risk == 'High' and user_experience == 'Expert':
            score += 0.1
        
        return round(min(score, 1.0), 2)
    
    def _generate_explanation(self, investment_type, user_profile):
        """Generate explanation for the recommendation"""
        explanations = {
            'Stocks': f"Stocks offer higher growth potential suitable for your {user_profile.get('yearsToRetirement', 30)}-year investment horizon.",
            'Bonds': f"Bonds provide stable, predictable returns that align with your {user_profile.get('riskTolerance', 'Medium').lower()} risk tolerance.",
            'ETF': f"ETFs offer diversification and lower fees, perfect for building a balanced portfolio over {user_profile.get('yearsToRetirement', 30)} years.",
            'Real Estate': f"Real estate investments provide inflation protection and steady growth for long-term wealth building."
        }
        
        return explanations.get(investment_type, f"{investment_type} investments align well with your financial goals and risk profile.")
    
    def _get_top_funds(self, investment_type, investments):
        """Get top performing funds for the investment type"""
        top_funds = investments.nlargest(3, 'Annual_Return_Rate')[['Fund_Name', 'Annual_Return_Rate', 'Fees_Percentage']].to_dict('records')
        
        return [{
            'name': fund['Fund_Name'],
            'return': round(fund['Annual_Return_Rate'], 2),
            'fees': round(fund['Fees_Percentage'], 2)
        } for fund in top_funds]
    
    def _get_default_recommendations(self):
        """Return default recommendations when data is not available"""
        return [
            {
                'investmentType': 'ETF',
                'averageReturn': 7.5,
                'riskLevel': 'Medium',
                'projectedValue': 500000,
                'fees': 0.8,
                'volatility': 3.2,
                'suitabilityScore': 0.85,
                'explanation': 'ETFs provide good diversification with lower fees, suitable for most investors.',
                'funds': [
                    {'name': 'Diversified Growth ETF', 'return': 8.2, 'fees': 0.7},
                    {'name': 'Balanced Index Fund', 'return': 7.8, 'fees': 0.9}
                ]
            },
            {
                'investmentType': 'Bonds',
                'averageReturn': 4.5,
                'riskLevel': 'Low',
                'projectedValue': 350000,
                'fees': 1.2,
                'volatility': 1.8,
                'suitabilityScore': 0.75,
                'explanation': 'Bonds offer stable returns with lower risk, ideal for conservative investors.',
                'funds': [
                    {'name': 'Government Bond Fund', 'return': 4.8, 'fees': 1.1},
                    {'name': 'Corporate Bond ETF', 'return': 4.2, 'fees': 1.3}
                ]
            }
        ]
    
    def get_market_trends(self):
        """Get current market trends and insights"""
        if self.df is None:
            return self._get_default_market_data()
        
        try:
            trends = {
                'topPerformingAssets': self._get_top_performing_assets(),
                'sectorAnalysis': self._get_sector_analysis(),
                'riskMetrics': self._get_risk_metrics(),
                'marketInsights': self._get_market_insights()
            }
            
            return trends
        except Exception as e:
            print(f"Error getting market trends: {e}")
            return self._get_default_market_data()
    
    def _get_top_performing_assets(self):
        """Get top performing investment funds"""
        top_funds = self.df.nlargest(5, 'Annual_Return_Rate')[
            ['Fund_Name', 'Annual_Return_Rate', 'Investment_Type', 'Volatility']
        ].to_dict('records')
        
        return [{
            'name': fund['Fund_Name'],
            'return': round(fund['Annual_Return_Rate'], 2),
            'type': fund['Investment_Type'],
            'volatility': round(fund['Volatility'], 2)
        } for fund in top_funds]
    
    def _get_sector_analysis(self):
        """Analyze performance by investment type"""
        sector_stats = self.df.groupby('Investment_Type').agg({
            'Annual_Return_Rate': ['mean', 'std'],
            'Fees_Percentage': 'mean',
            'Volatility': 'mean'
        }).round(2)
        
        return sector_stats.to_dict('index')
    
    def _get_risk_metrics(self):
        """Calculate market risk metrics"""
        return {
            'averageReturn': round(self.df['Annual_Return_Rate'].mean(), 2),
            'averageVolatility': round(self.df['Volatility'].mean(), 2),
            'averageFees': round(self.df['Fees_Percentage'].mean(), 2),
            'sharpeRatio': round(self.df['Annual_Return_Rate'].mean() / self.df['Volatility'].mean(), 2)
        }
    
    def _get_market_insights(self):
        """Generate market insights"""
        insights = []
        
        # Low fee funds insight
        low_fee_funds = self.df[self.df['Fees_Percentage'] < 1.0]
        if not low_fee_funds.empty:
            avg_return = low_fee_funds['Annual_Return_Rate'].mean()
            insights.append(f"Low-fee funds (< 1%) are delivering an average return of {avg_return:.1f}%")
        
        # High performing sectors
        best_sector = self.df.groupby('Investment_Type')['Annual_Return_Rate'].mean().idxmax()
        best_return = self.df.groupby('Investment_Type')['Annual_Return_Rate'].mean().max()
        insights.append(f"{best_sector} investments are currently the top performers with {best_return:.1f}% average returns")
        
        return insights
    
    def _get_default_market_data(self):
        """Default market data when CSV is not available"""
        return {
            'topPerformingAssets': [
                {'name': 'Growth ETF', 'return': 8.5, 'type': 'ETF', 'volatility': 3.2},
                {'name': 'Tech Stocks Fund', 'return': 8.2, 'type': 'Stocks', 'volatility': 4.1}
            ],
            'sectorAnalysis': {
                'ETF': {'return': 7.5, 'volatility': 3.2, 'fees': 0.8},
                'Stocks': {'return': 8.1, 'volatility': 4.2, 'fees': 1.2},
                'Bonds': {'return': 4.5, 'volatility': 1.8, 'fees': 1.1}
            },
            'riskMetrics': {
                'averageReturn': 6.8,
                'averageVolatility': 3.1,
                'averageFees': 1.0,
                'sharpeRatio': 2.2
            },
            'marketInsights': [
                'Low-fee ETFs are showing strong performance this year',
                'Diversified portfolios are outperforming single-asset strategies'
            ]
        }