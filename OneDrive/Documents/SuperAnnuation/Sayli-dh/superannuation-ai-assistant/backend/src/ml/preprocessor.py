"""
Preprocessor module:
- load dataset (csv/excel)
- cleaning, encoding, missing value handling
- feature engineering
- keeps LabelEncoders and scaler so they can be saved
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

logger = logging.getLogger(__name__)

DEFAULT_CATEGORICALS = [
    'Gender', 'Country', 'Employment_Status', 'Risk_Tolerance',
    'Contribution_Frequency', 'Investment_Type', 'Marital_Status',
    'Education_Level', 'Health_Status', 'Home_Ownership_Status',
    'Investment_Experience_Level', 'Financial_Goals', 'Pension_Type',
    'Withdrawal_Strategy', 'Transaction_Channel'
]

DEFAULT_BOOLEANS = [
    'Survivor_Benefits', 'Insurance_Coverage', 'Tax_Benefits_Eligibility',
    'Government_Pension_Eligibility', 'Private_Pension_Eligibility',
    'Suspicious_Flag', 'Previous_Fraud_Flag'
]

class Preprocessor:
    def __init__(self, categorical_cols=None, boolean_cols=None):
        self.categorical_cols = categorical_cols or DEFAULT_CATEGORICALS
        self.boolean_cols = boolean_cols or DEFAULT_BOOLEANS
        self.scaler = StandardScaler()
        self.label_encoders = {}   # col -> LabelEncoder
        self.feature_columns = []  # final feature list after fit

    def load(self, path):
        if path.endswith('.xlsx') or path.endswith('.xls'):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)
        return df

    def _safe_apply_labelencode_fit(self, series, col):
        le = LabelEncoder()
        # fill nans to 'NA' to keep classes stable
        ser = series.fillna('NA').astype(str)
        le.fit(ser)
        self.label_encoders[col] = le
        return le.transform(ser)

    def _safe_apply_labelencode_transform(self, series, col):
        le = self.label_encoders.get(col)
        ser = series.fillna('NA').astype(str)
        if le is None:
            # unseen: create temp encoder
            temp = LabelEncoder()
            temp.fit(ser)
            return temp.transform(ser)
        # transform, unseen -> new class handling: map to -1
        classes = set(le.classes_)
        mapped = []
        for v in ser:
            if v in classes:
                mapped.append(int(le.transform([v])[0]))
            else:
                mapped.append(-1)
        return np.array(mapped)

    def preprocess(self, df, fit=False):
        """
        fit=True  -> fit label encoders & scaler (for training)
        fit=False -> use saved encoders/scaler (for inference)
        returns processed dataframe
        """
        logger.info("Preprocessing start")
        data = df.copy()

        # Dates
        if 'Transaction_Date' in data.columns:
            data['Transaction_Date'] = pd.to_datetime(data['Transaction_Date'], errors='coerce')
            data['Transaction_Year'] = data['Transaction_Date'].dt.year.fillna(0).astype(int)
            data['Transaction_Month'] = data['Transaction_Date'].dt.month.fillna(0).astype(int)
            data['Transaction_Quarter'] = data['Transaction_Date'].dt.quarter.fillna(0).astype(int)

        # Categorical encoding
        for col in self.categorical_cols:
            if col in data.columns:
                if fit:
                    data[col] = self._safe_apply_labelencode_fit(data[col], col)
                else:
                    data[col] = self._safe_apply_labelencode_transform(data[col], col)

        # Boolean mapping
        for col in self.boolean_cols:
            if col in data.columns:
                data[col] = data[col].map({
                    'Yes': 1, 'No': 0, True: 1, False: 0,
                    'yes': 1, 'no': 0, 'Y': 1, 'N': 0
                }).fillna(0).astype(int)

        # Numeric missing handling
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols:
            if data[col].isnull().any():
                if col in ['Age', 'Annual_Income', 'Current_Savings']:
                    data[col] = data[col].fillna(data[col].median())
                else:
                    data[col] = data[col].fillna(0)

        # If fit -> create engineered features and fit scaler
        data = self._feature_engineering(data)

        if fit:
            # Fit scaler only on numeric features
            numeric_feats = data.select_dtypes(include=[np.number]).columns.tolist()
            self.feature_columns = numeric_feats
            self.scaler.fit(data[numeric_feats].values)
        else:
            # On inference ensure columns align: add missing numeric cols with zero
            for c in self.feature_columns:
                if c not in data.columns:
                    data[c] = 0

        # scale numeric features and return dataframe with scaled numeric columns
        numeric_feats = self.feature_columns
        if len(numeric_feats) > 0:
            scaled = self.scaler.transform(data[numeric_feats].values)
            data_scaled = pd.DataFrame(scaled, columns=numeric_feats, index=data.index)
            return data_scaled
        else:
            return data

    def _feature_engineering(self, data):
        """Implements the same feature engineering logic you had, defensive to missing columns."""
        df = data.copy()

        # safe getters
        get = lambda c, default=0: df[c] if c in df.columns else pd.Series([default]*len(df))

        # Age related
        if 'Age' not in df.columns and 'DOB' in df.columns:
            df['Age'] = (pd.Timestamp.now().year - pd.to_datetime(df['DOB'], errors='coerce').dt.year).fillna(0).astype(int)

        df['Retirement_Age_Goal'] = get('Retirement_Age_Goal', 65)
        df['Years_to_Retirement'] = np.maximum(df['Retirement_Age_Goal'] - get('Age', 0), 0)

        # Age group
        df['Age_Group'] = pd.cut(get('Age', 0), bins=[0,25,35,45,55,100], labels=[0,1,2,3,4]).astype(float).fillna(0)
        df['Age_Group'] = df['Age_Group'].astype(int)

        # Financial ratios (defensive)
        df['Annual_Income'] = get('Annual_Income', 0).astype(float)
        df['Total_Annual_Contribution'] = get('Total_Annual_Contribution', 0).astype(float)
        df['Current_Savings'] = get('Current_Savings', 0).astype(float)
        df['Debt_Level'] = get('Debt_Level', 0).astype(float)
        df['Monthly_Expenses'] = get('Monthly_Expenses', 0).astype(float)
        df['Annual_Return_Rate'] = get('Annual_Return_Rate', 0).astype(float)
        df['Fees_Percentage'] = get('Fees_Percentage', 0).astype(float)
        df['Volatility'] = get('Volatility', 0).astype(float)
        df['Savings_Rate'] = get('Savings_Rate', 0).astype(float)

        df['Contribution_Rate'] = np.where(df['Annual_Income'] > 0, df['Total_Annual_Contribution'] / df['Annual_Income'], 0)
        df['Savings_to_Income_Ratio'] = np.where(df['Annual_Income'] > 0, df['Current_Savings'] / df['Annual_Income'], 0)
        df['Debt_to_Income_Ratio'] = np.where(df['Annual_Income'] > 0, df['Debt_Level'] / df['Annual_Income'], 0)
        df['Expense_to_Income_Ratio'] = np.where(df['Annual_Income'] > 0, df['Monthly_Expenses'] * 12 / df['Annual_Income'], 0)

        # Investment features
        df['Risk_Adjusted_Return'] = np.where(df['Volatility'] > 0, df['Annual_Return_Rate'] / df['Volatility'], 0)
        df['Net_Return'] = df['Annual_Return_Rate'] - df['Fees_Percentage']
        df['Sharpe_Ratio'] = np.where(df['Volatility'] > 0, (df['Annual_Return_Rate'] - 2) / df['Volatility'], 0)

        df['Investment_Horizon'] = df['Years_to_Retirement']
        df['Contribution_Years_Remaining'] = np.maximum(df['Years_to_Retirement'] - 5, 0)
        # avoid negative rates: Annual_Return_Rate may be in percent or fraction
        df['Compound_Growth_Factor'] = np.power(1 + df['Annual_Return_Rate'] / np.where(df['Annual_Return_Rate'].abs() < 1e-6, 100, 100), df['Years_to_Retirement'])

        # Financial health score (bounded)
        savings_score = np.minimum(df.get('Savings_Rate', 0) * 10, 10)
        income_score = np.minimum(np.log1p(df['Annual_Income']) / np.log1p(200000) * 10, 10)
        debt_score = np.maximum(10 - df['Debt_to_Income_Ratio'] * 10, 0)
        df['Financial_Health_Score'] = (savings_score + income_score + debt_score) / 3

        # Risk mismatch (ensure Risk_Tolerance numeric)
        if 'Risk_Tolerance' in df.columns:
            # If risk tolerance is encoded string (e.g., Low/Medium/High), it's encoded earlier
            pass
        # risk_capacity heuristic
        df['Risk_Capacity'] = np.where(df['Years_to_Retirement'] > 20, 2, np.where(df['Years_to_Retirement'] > 10, 1, 0))
        # If Risk_Tolerance present but string, leave numeric mapping to label encoder.
        if 'Risk_Tolerance' in df.columns:
            try:
                df['Risk_Mismatch'] = np.abs(df['Risk_Tolerance'].astype(float) - df['Risk_Capacity'])
            except Exception:
                # Might be encoded later; set 0
                df['Risk_Mismatch'] = 0
        else:
            df['Risk_Mismatch'] = 0

        # Life stage
        df['Life_Stage'] = np.where(df['Age'] < 30, 0, np.where(df['Age'] < 50, 1, np.where(df['Age'] < 60, 2, 3)))

        # Final return
        return df
