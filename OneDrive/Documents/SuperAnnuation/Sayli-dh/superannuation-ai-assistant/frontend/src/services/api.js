import axios from 'axios';

// Create axios instance with base configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (if needed in future)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    
    // Handle specific error cases
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          throw new Error(data.error || 'Invalid request data');
        case 401:
          throw new Error('Unauthorized access');
        case 403:
          throw new Error('Access forbidden');
        case 404:
          throw new Error('Resource not found');
        case 500:
          throw new Error('Internal server error');
        default:
          throw new Error(data.error || 'An error occurred');
      }
    } else if (error.request) {
      // Network error
      throw new Error('Network error - please check your connection');
    } else {
      throw new Error('Request failed');
    }
  }
);

// API Functions

// Health check
export const healthCheck = async () => {
  return await api.get('/health');
};

// User Profile APIs
export const createUserProfile = async (profileData) => {
  return await api.post('/api/profile', profileData);
};

export const getUserProfile = async (userId) => {
  return await api.get(`/api/profile/${userId}`);
};

export const updateUserProfile = async (userId, profileData) => {
  return await api.put(`/api/profile/${userId}`, profileData);
};

// Chat APIs
export const sendChatMessage = async (message, userProfile = null, conversationHistory = []) => {
  return await api.post('/api/chat', {
    message,
    user_profile: userProfile,
    conversation_history: conversationHistory.map(msg => ({
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: msg.content
    }))
  });
};

// Recommendations APIs - UPDATED VERSION
export const getRecommendations = async (userProfile) => {
  // Transform frontend camelCase to backend PascalCase/snake_case
  const transformedProfile = {
    Age: userProfile.age || userProfile.Age,
    Annual_Income: userProfile.annualIncome || userProfile.Annual_Income,
    Current_Savings: userProfile.currentSavings || userProfile.Current_Savings || 0,
    Retirement_Age_Goal: userProfile.retirementAgeGoal || userProfile.Retirement_Age_Goal || 65,
    Risk_Tolerance: userProfile.riskTolerance || userProfile.Risk_Tolerance,
    Employment_Status: userProfile.employmentStatus || userProfile.Employment_Status || 'Full-time',
    Marital_Status: userProfile.maritalStatus || userProfile.Marital_Status || 'Single',
    Number_of_Dependents: userProfile.numberOfDependents || userProfile.Number_of_Dependents || 0
  };

  console.log('API sending transformed profile to backend:', transformedProfile);

  return await api.post('/api/recommendations', {
    user_profile: transformedProfile
  });
};

// Predictions APIs
export const getPredictions = async (userProfile, investmentAllocation) => {
  return await api.post('/api/predict', {
    user_profile: userProfile,
    investment_allocation: investmentAllocation
  });
};

// Market Analysis APIs
export const getMarketAnalysis = async () => {
  return await api.get('/api/market-analysis');
};

// Educational Content APIs
export const getEducationalContent = async (topic, level = 'beginner') => {
  return await api.get('/api/education', {
    params: { topic, level }
  });
};

// Utility functions for data processing

export const formatCurrency = (amount, currency = 'AUD') => {
  if (amount >= 1000000) {
    return `$${(amount / 1000000).toFixed(1)}M ${currency}`;
  } else if (amount >= 1000) {
    return `$${(amount / 1000).toFixed(0)}K ${currency}`;
  }
  return `$${amount.toLocaleString()} ${currency}`;
};

export const formatPercentage = (rate, decimalPlaces = 1) => {
  return `${(rate * 100).toFixed(decimalPlaces)}%`;
};

export const calculateRetirementYears = (currentAge, retirementAge = 65) => {
  return Math.max(0, retirementAge - currentAge);
};

// Mock data generators (for development/demo purposes)
export const generateMockRecommendations = (userProfile) => {
  const age = userProfile?.age || 35;
  const riskTolerance = userProfile?.risk_tolerance || userProfile?.riskTolerance || 'Medium';
  
  return {
    user_summary: {
      age: age,
      time_horizon: Math.max(0, 65 - age),
      risk_profile: riskTolerance.toLowerCase(),
      current_balance: userProfile?.current_savings || userProfile?.currentSavings || 50000
    },
    asset_allocation: {
      'Australian Shares': riskTolerance === 'High' ? 0.5 : riskTolerance === 'Low' ? 0.2 : 0.35,
      'International Shares': riskTolerance === 'High' ? 0.3 : riskTolerance === 'Low' ? 0.15 : 0.25,
      'Australian Bonds': riskTolerance === 'High' ? 0.1 : riskTolerance === 'Low' ? 0.5 : 0.25,
      'International Bonds': riskTolerance === 'High' ? 0.05 : riskTolerance === 'Low' ? 0.1 : 0.1,
      'Property/REITs': 0.05,
      'Cash': 0.02
    },
    recommended_investments: {
      primary_recommendation: {
        name: riskTolerance === 'High' ? 'High Growth' : riskTolerance === 'Low' ? 'Conservative Balanced' : 'Balanced Growth',
        type: 'Pre-mixed Option',
        allocation: 100,
        expected_return: riskTolerance === 'High' ? 8.2 : riskTolerance === 'Low' ? 4.8 : 6.8,
        volatility: riskTolerance === 'High' ? 16.5 : riskTolerance === 'Low' ? 8.2 : 12.8,
        fees: 0.75,
        description: riskTolerance === 'High' 
          ? 'Growth-focused option maximizing long-term capital appreciation'
          : riskTolerance === 'Low'
            ? 'Lower risk balanced option with focus on capital preservation'
            : 'Balanced approach between growth and stability',
        suitability: riskTolerance === 'High'
          ? 'Suitable for long-term investors comfortable with market volatility'
          : riskTolerance === 'Low'
            ? 'Ideal for investors seeking steady, predictable growth with lower volatility'
            : 'Good all-round option for most investors with moderate risk tolerance'
      },
      alternative_options: [
        {
          name: 'Index Diversified',
          type: 'Index Option',
          expected_return: riskTolerance === 'High' ? 7.9 : riskTolerance === 'Low' ? 4.5 : 6.5,
          fees: 0.15,
          description: 'Low-cost diversified index option',
          benefits: ['Very low fees', 'Broad diversification', 'Simple to understand']
        }
      ]
    },
    projections: {
      time_horizon_years: Math.max(0, 65 - age),
      scenarios: {
        conservative: {
          final_balance: (userProfile?.current_savings || userProfile?.currentSavings || 50000) * 3,
          annual_retirement_income: ((userProfile?.current_savings || userProfile?.currentSavings || 50000) * 3) * 0.04,
          return_assumption: 0.05
        },
        expected: {
          final_balance: (userProfile?.current_savings || userProfile?.currentSavings || 50000) * 5,
          annual_retirement_income: ((userProfile?.current_savings || userProfile?.currentSavings || 50000) * 5) * 0.04,
          return_assumption: 0.07
        },
        optimistic: {
          final_balance: (userProfile?.current_savings || userProfile?.currentSavings || 50000) * 8,
          annual_retirement_income: ((userProfile?.current_savings || userProfile?.currentSavings || 50000) * 8) * 0.04,
          return_assumption: 0.09
        }
      }
    },
    explanation: `Based on your ${riskTolerance.toLowerCase()} risk tolerance and ${Math.max(0, 65 - age)} years until retirement, this strategy balances growth potential with appropriate risk management.`,
    next_steps: [
      'Review your current super fund\'s investment options and fees',
      'Consider consolidating multiple super accounts to reduce fees',
      age > 50 ? 'Review your insurance coverage within super' : 'Focus on low-fee investment options to maximize long-term growth',
      'Schedule an annual review of your super strategy'
    ]
  };
};

export const generateMockMarketAnalysis = () => {
  return {
    market_summary: {
      australian_shares: {
        current_trend: 'Positive',
        ytd_return: 8.2,
        outlook: 'Moderate growth expected driven by resource sector and domestic demand'
      },
      international_shares: {
        current_trend: 'Mixed',
        ytd_return: 12.1,
        outlook: 'Continued volatility expected due to inflation concerns and geopolitical tensions'
      },
      bonds: {
        current_trend: 'Stabilizing',
        ytd_return: -2.1,
        outlook: 'Interest rate peaks may provide opportunities for bond investors'
      },
      property: {
        current_trend: 'Stable',
        ytd_return: 6.8,
        outlook: 'Defensive characteristics attractive in uncertain environment'
      }
    },
    key_themes: [
      'Inflation moderating but still above target ranges',
      'Central bank policy normalization continuing',
      'Geopolitical tensions affecting global markets',
      'ESG investing gaining mainstream adoption',
      'Technology disruption creating opportunities and risks'
    ],
    recommendations: [
      'Maintain diversified portfolio across asset classes',
      'Consider defensive positions given market uncertainty',
      'Focus on quality investments with sustainable business models',
      'Regular rebalancing remains important'
    ]
  };
};

// Error handling helper
export const handleApiError = (error, fallbackMessage = 'An error occurred') => {
  console.error('API Error:', error);
  
  if (error.response?.data?.error) {
    return error.response.data.error;
  } else if (error.message) {
    return error.message;
  } else {
    return fallbackMessage;
  }
};

// Local storage helpers for caching
export const setCachedData = (key, data, expiryMinutes = 30) => {
  const expiryTime = new Date().getTime() + (expiryMinutes * 60000);
  const cacheData = {
    data: data,
    expiry: expiryTime
  };
  localStorage.setItem(key, JSON.stringify(cacheData));
};

export const getCachedData = (key) => {
  try {
    const cached = localStorage.getItem(key);
    if (!cached) return null;
    
    const cacheData = JSON.parse(cached);
    const now = new Date().getTime();
    
    if (now > cacheData.expiry) {
      localStorage.removeItem(key);
      return null;
    }
    
    return cacheData.data;
  } catch (error) {
    console.error('Cache error:', error);
    return null;
  }
};

export default api;