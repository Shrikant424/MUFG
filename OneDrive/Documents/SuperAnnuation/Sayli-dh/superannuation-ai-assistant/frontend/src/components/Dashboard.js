import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  IconButton,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  AccountBalance as BalanceIcon,
  Timeline as TimelineIcon,
  TrackChanges as TargetIcon,   // ✅ replace Target with TrackChanges
  Lightbulb as LightbulbIcon,
  Refresh as RefreshIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

// Fixed import path - assuming api.js is in services folder or adjust accordingly
import { getRecommendations, getMarketAnalysis, generateMockRecommendations, generateMockMarketAnalysis } from '../services/api';

const Dashboard = ({ userProfile }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [marketAnalysis, setMarketAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, [userProfile]);

  const loadDashboardData = async () => {
    if (!userProfile) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      
      // Transform userProfile to match backend format before sending to API
      const transformedProfile = {
        Age: userProfile.age,
        Annual_Income: userProfile.annual_income || userProfile.annualIncome,
        Current_Savings: userProfile.current_savings || userProfile.currentSavings || 0,
        Retirement_Age_Goal: userProfile.retirement_age_goal || userProfile.retirementAgeGoal || 65,
        Risk_Tolerance: userProfile.risk_tolerance || userProfile.riskTolerance,
        Employment_Status: userProfile.employment_status || userProfile.employmentStatus || 'Full-time',
        Marital_Status: userProfile.marital_status || userProfile.maritalStatus || 'Single',
        Number_of_Dependents: userProfile.number_of_dependents || userProfile.numberOfDependents || 0
      };

      console.log('Dashboard sending transformed profile:', transformedProfile);
      
      // Try API first, fall back to mock data if API fails
      try {
        const [recsResponse, marketResponse] = await Promise.all([
          getRecommendations(transformedProfile),
          getMarketAnalysis()
        ]);
        setRecommendations(recsResponse.recommendations || recsResponse);
        setMarketAnalysis(marketResponse.analysis || marketResponse);
      } catch (apiError) {
        console.warn('API unavailable, using mock data:', apiError);
        // Use mock data as fallback
        const mockRecs = generateMockRecommendations(userProfile);
        const mockMarket = generateMockMarketAnalysis();
        setRecommendations(mockRecs);
        setMarketAnalysis(mockMarket);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (!userProfile) {
    return (
      <Box textAlign="center" py={8}>
        <Typography variant="h5" gutterBottom>
          Welcome to Your Superannuation Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Please complete your profile to get personalized recommendations
        </Typography>
        <Button 
          variant="contained" 
          size="large" 
          onClick={() => navigate('/profile')}
          sx={{ mt: 2 }}
        >
          Complete Profile
        </Button>
      </Box>
    );
  }

  const currentAge = userProfile.age || 30;
  const retirementAge = userProfile.retirement_age_goal || userProfile.retirementAgeGoal || 65;
  const yearsToRetirement = Math.max(0, retirementAge - currentAge);
  const currentBalance = userProfile.current_savings || userProfile.currentSavings || 0;
  const annualIncome = userProfile.annual_income || userProfile.annualIncome || 0;

  // Calculate retirement progress
  const retirementProgress = Math.min(100, ((currentAge - 25) / (retirementAge - 25)) * 100);

  // Quick stats cards
  const statsCards = [
    {
      title: 'Current Balance',
      value: `$${currentBalance.toLocaleString()}`,
      icon: <BalanceIcon />,
      color: 'primary',
      subtitle: 'Superannuation balance'
    },
    {
      title: 'Years to Retirement',
      value: yearsToRetirement,
      icon: <TimelineIcon />,
      color: 'secondary',
      subtitle: `Target age: ${retirementAge}`
    },
    {
      title: 'Annual Income',
      value: `$${annualIncome.toLocaleString()}`,
      icon: <TrendingUpIcon />,
      color: 'success',
      subtitle: 'Current salary'
    },
    {
      title: 'Risk Profile',
      value: userProfile.risk_tolerance || userProfile.riskTolerance || 'Not Set',
      icon: <TargetIcon />,
      color: 'warning',
      subtitle: 'Investment preference'
    }
  ];

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Dashboard
        </Typography>
        <Box>
          <IconButton onClick={loadDashboardData} disabled={loading}>
            <RefreshIcon />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<ChatIcon />}
            onClick={() => navigate('/chat')}
            sx={{ ml: 1 }}
          >
            Ask AI Advisor
          </Button>
        </Box>
      </Box>

      {/* Quick Stats */}
      <Grid container spacing={3} mb={4}>
        {statsCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Avatar sx={{ bgcolor: `${card.color}.main`, mr: 2 }}>
                    {card.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h6" color={`${card.color}.main`}>
                      {card.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {card.title}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {card.subtitle}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Retirement Progress */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Retirement Journey Progress
              </Typography>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">
                    Age {currentAge} → {retirementAge}
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {retirementProgress.toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={retirementProgress} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                {yearsToRetirement > 0 
                  ? `${yearsToRetirement} years remaining until your target retirement age`
                  : 'You have reached your target retirement age!'
                }
              </Typography>
            </CardContent>
          </Card>

          {/* Simplified Performance Chart Placeholder */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Portfolio Performance Projection
              </Typography>
              <Box 
                height={300} 
                display="flex" 
                alignItems="center" 
                justifyContent="center"
                bgcolor="grey.50"
                borderRadius={1}
              >
                <Typography variant="body2" color="text.secondary">
                  Performance chart will be displayed here
                  <br />
                  (PerformanceChart component needed)
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Loading State */}
          {loading && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box textAlign="center" py={2}>
                  <CircularProgress />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Loading recommendations...
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Current Recommendations */}
          {recommendations && recommendations.recommended_investments && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Current Recommendation
                </Typography>
                {recommendations.recommended_investments.primary_recommendation && (
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                      {recommendations.recommended_investments.primary_recommendation.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {recommendations.recommended_investments.primary_recommendation.description}
                    </Typography>
                    <Box display="flex" gap={1} mb={2}>
                      <Chip 
                        size="small" 
                        label={`${recommendations.recommended_investments.primary_recommendation.expected_return}% return`}
                        color="success" 
                      />
                      <Chip 
                        size="small" 
                        label={`${recommendations.recommended_investments.primary_recommendation.fees}% fees`}
                        variant="outlined" 
                      />
                    </Box>
                    <Button 
                      size="small" 
                      onClick={() => navigate('/recommendations')}
                    >
                      View Details
                    </Button>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}

          {/* Market Insights */}
          {marketAnalysis && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Insights
                </Typography>
                {marketAnalysis.key_themes && (
                  <Box>
                    {marketAnalysis.key_themes.slice(0, 3).map((theme, index) => (
                      <Box key={index} mb={1}>
                        <Typography variant="body2" color="text.secondary">
                          • {theme}
                        </Typography>
                      </Box>
                    ))}
                    <Button size="small" sx={{ mt: 1 }}>
                      View Full Analysis
                    </Button>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}

          {/* Action Items */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommended Actions
              </Typography>
              
              {recommendations?.next_steps && (
                <Box>
                  {recommendations.next_steps.slice(0, 4).map((step, index) => (
                    <Box key={index} display="flex" alignItems="flex-start" mb={2}>
                      <LightbulbIcon color="primary" sx={{ mr: 1, mt: 0.5, fontSize: 16 }} />
                      <Typography variant="body2">{step}</Typography>
                    </Box>
                  ))}
                </Box>
              )}

              {!recommendations && !loading && (
                <Box textAlign="center" py={2}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Complete your profile to get recommendations
                  </Typography>
                  <Button 
                    size="small" 
                    onClick={() => navigate('/profile')}
                  >
                    Go to Profile
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ mt: 4, p: 3, bgcolor: 'primary.50' }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<ChatIcon />}
              onClick={() => navigate('/chat')}
            >
              Ask AI Advisor
            </Button>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<TargetIcon />}
              onClick={() => navigate('/recommendations')}
            >
              View Recommendations
            </Button>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<TrendingUpIcon />}
              onClick={() => navigate('/profile')}
            >
              Update Profile
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default Dashboard;