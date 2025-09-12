import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import logging
from typing import Dict, List, Tuple, Any
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class SuperannuationPredictor:
    """Machine Learning model for predicting superannuation outcomes"""
    
    def __init__(self):
        self.pension_model = None
        self.return_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
        self.model_metrics = {}
        
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train the ML models on superannuation data"""
        try:
            logger.info("Starting model training...")
            
            # Prepare features and targets
            X, y_pension, y_return = self._prepare_features(data)
            
            if X.empty:
                logger.error("No valid features found for training")
                return {'error': 'No valid features for training'}
            
            # Split data
            X_train, X_test, y_pension_train, y_pension_test, y_return_train, y_return_test = train_test_split(
                X, y_pension, y_return, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train pension amount prediction model
            self.pension_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            self.pension_model.fit(X_train_scaled, y_pension_train)
            
            # Train return prediction model
            self.return_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                random_state=42
            )
            self.return_model.fit(X_train_scaled, y_return_train)
            
            # Evaluate models
            pension_pred = self.pension_model.predict(X_test_scaled)
            return_pred = self.return_model.predict(X_test_scaled)
            
            # Calculate metrics
            self.model_metrics = {
                'pension_model': {
                    'mae': mean_absolute_error(y_pension_test, pension_pred),
                    'mse': mean_squared_error(y_pension_test, pension_pred),
                    'r2': r2_score(y_pension_test, pension_pred)
                },
                'return_model': {
                    'mae': mean_absolute_error(y_return_test, return_pred),
                    'mse': mean_squared_error(y_return_test, return_pred),
                    'r2': r2_score(y_return_test, return_pred)
                }
            }
            
            self.is_trained = True
            logger.info("Model training completed successfully")
            
            # Save models
            self._save_models()
            
            return {
                'success': True,
                'metrics': self.model_metrics,
                'features_used': len(self.feature_columns),
                'training_samples': len(X_train)
            }
            
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            return {'error': str(e)}
    
    def _prepare_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """Prepare features and target variables"""
        
        # Define feature columns
        numerical_features = [
            'Age', 'Annual_Income', 'Current_Savings', 'Retirement_Age_Goal',
            'Contribution_Amount', 'Years_Contributed', 'Annual_Return_Rate',
            'Volatility', 'Fees_Percentage', 'Number_of_Dependents',
            'Life_Expectancy_Estimate', 'Debt_Level', 'Monthly_Expenses',
            'Savings_Rate', 'Portfolio_Diversity_Score'
        ]
        
        categorical_features = [
            'Gender', 'Country', 'Employment_Status', 'Risk_Tolerance',
            'Contribution_Frequency', 'Investment_Type', 'Marital_Status',
            'Education_Level', 'Health_Status', 'Home_Ownership_Status',
            'Investment_Experience_Level', 'Pension_Type'
        ]
        
        # Create feature matrix
        X = pd.DataFrame()
        
        # Add numerical features
        for feature in numerical_features:
            if feature in data.columns:
                X[feature] = pd.to_numeric(data[feature], errors='coerce')
        
        # Encode categorical features
        for feature in categorical_features:
            if feature in data.columns:
                if feature not in self.label_encoders:
                    self.label_encoders[feature] = LabelEncoder()
                    
                # Handle missing values
                feature_data = data[feature].fillna('Unknown')
                
                try:
                    X[feature] = self.label_encoders[feature].fit_transform(feature_data)
                except ValueError:
                    # Handle unseen categories
                    X[feature] = 0
        
        # Create derived features
        X['Years_To_Retirement'] = X.get('Retirement_Age_Goal', 65) - X.get('Age', 35)
        X['Income_To_Savings_Ratio'] = X.get('Annual_Income', 1) / (X.get('Current_Savings', 1) + 1)
        X['Contribution_Rate'] = X.get('Contribution_Amount', 0) / (X.get('Annual_Income', 1) + 1)
        
        # Fill missing values
        X = X.fillna(X.median())
        
        # Store feature columns
        self.feature_columns = X.columns.tolist()
        
        # Define target variables
        y_pension = pd.to_numeric(data.get('Projected_Pension_Amount', 0), errors='coerce').fillna(0)
        y_return = pd.to_numeric(data.get('Annual_Return_Rate', 0.05), errors='coerce').fillna(0.05)
        
        return X, y_pension, y_return
    
    def predict_future_value(self, user_profile: Dict, investment_allocation: Dict) -> Dict[str, Any]:
        """Predict future superannuation value based on user profile and investment choices"""
        try:
            if not self.is_trained:
                logger.warning("Model not trained, using fallback predictions")
                return self._fallback_predictions(user_profile, investment_allocation)
            
            # Convert user profile to feature vector
            features = self._profile_to_features(user_profile, investment_allocation)
            
            if features is None:
                return self._fallback_predictions(user_profile, investment_allocation)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Make predictions
            predicted_pension = self.pension_model.predict(features_scaled)[0]
            predicted_return = self.return_model.predict(features_scaled)[0]
            
            # Calculate additional metrics
            current_age = user_profile.get('age', 35)
            retirement_age = user_profile.get('retirement_age_goal', 65)
            years_to_retirement = max(1, retirement_age - current_age)
            current_balance = user_profile.get('current_savings', 50000)
            annual_income = user_profile.get('annual_income', 70000)
            
            # Calculate scenarios
            scenarios = self._calculate_scenarios(
                current_balance, annual_income, predicted_return, years_to_retirement
            )
            
            # Calculate required contributions for goals
            contribution_analysis = self._analyze_contributions(
                current_balance, annual_income, predicted_return, years_to_retirement
            )
            
            return {
                'predictions': {
                    'projected_final_balance': max(0, predicted_pension),
                    'expected_annual_return': max(0, min(0.15, predicted_return)),
                    'years_to_retirement': years_to_retirement
                },
                'scenarios': scenarios,
                'contribution_analysis': contribution_analysis,
                'model_confidence': self._calculate_confidence(features),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            return self._fallback_predictions(user_profile, investment_allocation)
    
    def _profile_to_features(self, user_profile: Dict, investment_allocation: Dict) -> List[float]:
        """Convert user profile to feature vector"""
        try:
            features = []
            
            # Map user profile to expected features
            feature_mapping = {
                'Age': user_profile.get('age', 35),
                'Annual_Income': user_profile.get('annual_income', 70000),
                'Current_Savings': user_profile.get('current_savings', 50000),
                'Retirement_Age_Goal': user_profile.get('retirement_age_goal', 65),
                'Contribution_Amount': user_profile.get('annual_income', 70000) * 0.11,  # Default employer contribution
                'Years_Contributed': max(1, user_profile.get('age', 35) - 22),  # Assume started at 22
                'Annual_Return_Rate': self._estimate_return_from_allocation(investment_allocation),
                'Volatility': self._estimate_volatility_from_allocation(investment_allocation),
                'Fees_Percentage': 0.75,  # Default fee
                'Number_of_Dependents': user_profile.get('dependents', 0),
                'Life_Expectancy_Estimate': 85,  # Default
                'Debt_Level': user_profile.get('annual_income', 70000) * 0.3,  # Estimate
                'Monthly_Expenses': user_profile.get('annual_income', 70000) * 0.6 / 12,  # Estimate
                'Savings_Rate': 0.15,  # Default
                'Portfolio_Diversity_Score': 0.8  # Default
            }
            
            # Categorical mappings
            categorical_mapping = {
                'Gender': {'Male': 0, 'Female': 1, 'Other': 2}.get(user_profile.get('gender', 'Male'), 0),
                'Country': {'Australia': 0, 'UK': 1, 'USA': 2, 'Canada': 3, 'Germany': 4}.get(user_profile.get('country', 'Australia'), 0),
                'Employment_Status': {'Full-time': 0, 'Part-time': 1, 'Self-employed': 2, 'Unemployed': 3, 'Retired': 4}.get(user_profile.get('employment_status', 'Full-time'), 0),
                'Risk_Tolerance': {'Low': 0, 'Medium': 1, 'High': 2}.get(user_profile.get('risk_tolerance', 'Medium'), 1),
                'Contribution_Frequency': 0,  # Default
                'Investment_Type': 0,  # Default
                'Marital_Status': {'Single': 0, 'Married': 1, 'Divorced': 2, 'Widowed': 3}.get(user_profile.get('marital_status', 'Single'), 0),
                'Education_Level': 1,  # Default
                'Health_Status': 1,  # Default
                'Home_Ownership_Status': 1,  # Default
                'Investment_Experience_Level': 1,  # Default
                'Pension_Type': 1  # Default
            }
            
            # Build feature vector in the same order as training
            feature_vector = []
            for col in self.feature_columns:
                if col in feature_mapping:
                    feature_vector.append(feature_mapping[col])
                elif col in categorical_mapping:
                    feature_vector.append(categorical_mapping[col])
                elif col == 'Years_To_Retirement':
                    feature_vector.append(max(1, user_profile.get('retirement_age_goal', 65) - user_profile.get('age', 35)))
                elif col == 'Income_To_Savings_Ratio':
                    savings = user_profile.get('current_savings', 50000) + 1
                    income = user_profile.get('annual_income', 70000)
                    feature_vector.append(income / savings)
                elif col == 'Contribution_Rate':
                    income = user_profile.get('annual_income', 70000) + 1
                    contribution = income * 0.11  # Default employer contribution
                    feature_vector.append(contribution / income)
                else:
                    feature_vector.append(0)  # Default for unknown features
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error converting profile to features: {str(e)}")
            return None
    
    def _estimate_return_from_allocation(self, allocation: Dict) -> float:
        """Estimate expected return based on asset allocation"""
        expected_returns = {
            'Australian Shares': 0.085,
            'International Shares': 0.082,
            'Australian Bonds': 0.042,
            'International Bonds': 0.038,
            'Property/REITs': 0.076,
            'Cash': 0.025
        }
        
        total_return = 0
        total_allocation = 0
        
        for asset, weight in allocation.items():
            if asset in expected_returns:
                total_return += weight * expected_returns[asset]
                total_allocation += weight
        
        return total_return / max(total_allocation, 1)
    
    def _estimate_volatility_from_allocation(self, allocation: Dict) -> float:
        """Estimate portfolio volatility based on asset allocation"""
        volatilities = {
            'Australian Shares': 0.16,
            'International Shares': 0.17,
            'Australian Bonds': 0.06,
            'International Bonds': 0.07,
            'Property/REITs': 0.14,
            'Cash': 0.01
        }
        
        # Simplified volatility calculation (doesn't account for correlations)
        total_vol = 0
        total_allocation = 0
        
        for asset, weight in allocation.items():
            if asset in volatilities:
                total_vol += (weight ** 2) * (volatilities[asset] ** 2)
                total_allocation += weight
        
        return (total_vol / max(total_allocation, 1)) ** 0.5
    
    def _calculate_scenarios(self, current_balance: float, annual_income: float, 
                           expected_return: float, years: int) -> Dict:
        """Calculate different projection scenarios"""
        
        annual_contribution = annual_income * 0.11  # Employer contribution
        
        scenarios = {}
        
        for scenario, return_multiplier in [('pessimistic', 0.6), ('expected', 1.0), ('optimistic', 1.4)]:
            scenario_return = expected_return * return_multiplier
            
            # Calculate future value
            fv = self._future_value_with_payments(
                current_balance, annual_contribution, scenario_return, years
            )
            
            scenarios[scenario] = {
                'final_balance': fv,
                'annual_retirement_income': fv * 0.04,  # 4% withdrawal rule
                'return_assumption': scenario_return
            }
        
        return scenarios
    
    def _future_value_with_payments(self, pv: float, pmt: float, rate: float, years: int) -> float:
        """Calculate future value with regular payments"""
        if rate == 0:
            return pv + (pmt * years)
        
        fv_pv = pv * ((1 + rate) ** years)
        fv_pmt = pmt * (((1 + rate) ** years - 1) / rate)
        
        return fv_pv + fv_pmt
    
    def _analyze_contributions(self, current_balance: float, annual_income: float, 
                             expected_return: float, years: int) -> Dict:
        """Analyze required contributions for different retirement goals"""
        
        # Define retirement income targets
        income_replacement_targets = [0.6, 0.7, 0.8]  # 60%, 70%, 80% of current income
        
        analysis = {}
        
        for target_pct in income_replacement_targets:
            target_annual_income = annual_income * target_pct
            required_balance = target_annual_income / 0.04  # 4% withdrawal rule
            
            # Calculate required annual contribution
            employer_contribution = annual_income * 0.11
            
            # Calculate additional contribution needed
            fv_current = current_balance * ((1 + expected_return) ** years)
            fv_employer = employer_contribution * (((1 + expected_return) ** years - 1) / expected_return) if expected_return > 0 else employer_contribution * years
            
            shortfall = required_balance - fv_current - fv_employer
            
            if shortfall > 0 and expected_return > 0:
                additional_annual_contribution = shortfall * expected_return / ((1 + expected_return) ** years - 1)
            else:
                additional_annual_contribution = 0
            
            analysis[f"{int(target_pct * 100)}%_replacement"] = {
                'target_retirement_income': target_annual_income,
                'required_balance': required_balance,
                'projected_balance_current_path': fv_current + fv_employer,
                'shortfall': max(0, shortfall),
                'additional_annual_contribution_needed': max(0, additional_annual_contribution),
                'additional_monthly_contribution_needed': max(0, additional_annual_contribution / 12)
            }
        
        return analysis
    
    def _calculate_confidence(self, features: List[float]) -> Dict:
        """Calculate model confidence based on feature similarity to training data"""
        try:
            # Simple confidence metric based on model performance
            pension_r2 = self.model_metrics.get('pension_model', {}).get('r2', 0.5)
            return_r2 = self.model_metrics.get('return_model', {}).get('r2', 0.5)
            
            avg_confidence = (pension_r2 + return_r2) / 2
            
            return {
                'overall_confidence': max(0, min(1, avg_confidence)),
                'confidence_level': 'High' if avg_confidence > 0.8 else 'Medium' if avg_confidence > 0.6 else 'Low',
                'pension_model_r2': pension_r2,
                'return_model_r2': return_r2
            }
        except:
            return {
                'overall_confidence': 0.7,
                'confidence_level': 'Medium',
                'pension_model_r2': 0.7,
                'return_model_r2': 0.7
            }
    
    def _fallback_predictions(self, user_profile: Dict, investment_allocation: Dict) -> Dict:
        """Provide fallback predictions when ML model is unavailable"""
        
        current_age = user_profile.get('age', 35)
        retirement_age = user_profile.get('retirement_age_goal', 65)
        years_to_retirement = max(1, retirement_age - current_age)
        current_balance = user_profile.get('current_savings', 50000)
        annual_income = user_profile.get('annual_income', 70000)
        
        # Use simple compound interest calculation
        annual_contribution = annual_income * 0.11
        expected_return = 0.07  # Conservative assumption
        
        # Calculate future value
        final_balance = self._future_value_with_payments(
            current_balance, annual_contribution, expected_return, years_to_retirement
        )
        
        return {
            'predictions': {
                'projected_final_balance': final_balance,
                'expected_annual_return': expected_return,
                'years_to_retirement': years_to_retirement
            },
            'scenarios': {
                'pessimistic': {
                    'final_balance': final_balance * 0.7,
                    'annual_retirement_income': final_balance * 0.7 * 0.04,
                    'return_assumption': expected_return * 0.7
                },
                'expected': {
                    'final_balance': final_balance,
                    'annual_retirement_income': final_balance * 0.04,
                    'return_assumption': expected_return
                },
                'optimistic': {
                    'final_balance': final_balance * 1.3,
                    'annual_retirement_income': final_balance * 1.3 * 0.04,
                    'return_assumption': expected_return * 1.3
                }
            },
            'contribution_analysis': self._analyze_contributions(
                current_balance, annual_income, expected_return, years_to_retirement
            ),
            'model_confidence': {
                'overall_confidence': 0.6,
                'confidence_level': 'Medium (Fallback)',
                'note': 'Using simplified calculations - complete profile for better accuracy'
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from trained models"""
        if not self.is_trained or not hasattr(self.pension_model, 'feature_importances_'):
            return {}
        
        try:
            importance_data = []
            
            for i, feature in enumerate(self.feature_columns):
                pension_importance = self.pension_model.feature_importances_[i]
                return_importance = self.return_model.feature_importances_[i]
                
                importance_data.append({
                    'feature': feature,
                    'pension_importance': pension_importance,
                    'return_importance': return_importance,
                    'avg_importance': (pension_importance + return_importance) / 2
                })
            
            # Sort by average importance
            importance_data.sort(key=lambda x: x['avg_importance'], reverse=True)
            
            return {
                'feature_importance': importance_data[:10],  # Top 10 features
                'model_type': 'GradientBoosting + RandomForest'
            }
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return {}
    
    def _save_models(self):
        """Save trained models and preprocessors"""
        try:
            os.makedirs('models', exist_ok=True)
            
            if self.pension_model:
                joblib.dump(self.pension_model, 'models/pension_model.joblib')
            if self.return_model:
                joblib.dump(self.return_model, 'models/return_model.joblib')
            
            joblib.dump(self.scaler, 'models/scaler.joblib')
            joblib.dump(self.label_encoders, 'models/label_encoders.joblib')
            joblib.dump(self.feature_columns, 'models/feature_columns.joblib')
            
            # Save metadata
            metadata = {
                'training_date': datetime.now().isoformat(),
                'model_metrics': self.model_metrics,
                'feature_count': len(self.feature_columns),
                'is_trained': self.is_trained
            }
            joblib.dump(metadata, 'models/model_metadata.joblib')
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            if os.path.exists('models/pension_model.joblib'):
                self.pension_model = joblib.load('models/pension_model.joblib')
                self.return_model = joblib.load('models/return_model.joblib')
                self.scaler = joblib.load('models/scaler.joblib')
                self.label_encoders = joblib.load('models/label_encoders.joblib')
                self.feature_columns = joblib.load('models/feature_columns.joblib')
                
                metadata = joblib.load('models/model_metadata.joblib')
                self.model_metrics = metadata.get('model_metrics', {})
                self.is_trained = metadata.get('is_trained', False)
                
                logger.info("Models loaded successfully")
                return True
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            
        return False
    
    def evaluate_portfolio(self, user_profile: Dict, allocation: Dict) -> Dict:
        """Evaluate a specific portfolio allocation for the user"""
        
        # Calculate expected return and risk
        expected_return = self._estimate_return_from_allocation(allocation)
        volatility = self._estimate_volatility_from_allocation(allocation)
        
        # Risk-adjusted return (Sharpe ratio approximation)
        risk_free_rate = 0.025  # Approximate cash rate
        sharpe_ratio = (expected_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Age-based risk appropriateness
        age = user_profile.get('age', 35)
        years_to_retirement = user_profile.get('retirement_age_goal', 65) - age
        
        # Calculate risk score (0-100)
        if years_to_retirement > 20:
            target_volatility = 0.15  # Can handle higher risk
        elif years_to_retirement > 10:
            target_volatility = 0.12
        else:
            target_volatility = 0.08
        
        risk_appropriateness = max(0, min(100, 100 - abs(volatility - target_volatility) * 500))
        
        return {
            'allocation': allocation,
            'expected_annual_return': expected_return,
            'estimated_volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'risk_appropriateness_score': risk_appropriateness,
            'suitability_rating': 'High' if risk_appropriateness > 80 else 'Medium' if risk_appropriateness > 60 else 'Low',
            'recommendation': self._get_portfolio_recommendation(expected_return, volatility, risk_appropriateness)
        }
    
    def _get_portfolio_recommendation(self, expected_return: float, volatility: float, 
                                    risk_score: float) -> str:
        """Generate recommendation text for portfolio evaluation"""
        
        if risk_score > 80:
            return "This allocation appears well-suited to your risk profile and time horizon. Consider implementing this strategy."
        elif risk_score > 60:
            return "This allocation is reasonable but could be optimized. Consider adjusting the risk level slightly."
        else:
            return "This allocation may not be optimal for your situation. Consider reviewing your risk tolerance and time horizon."