import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import InvestmentRecommendations from '../components/InvestmentRecommendations.js';


const Recommendations = ({ userProfile }) => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Investment Recommendations
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          AI-powered investment recommendations tailored to your risk profile and retirement goals.
        </Typography>
        
        <InvestmentRecommendations userProfile={userProfile} />
      </Box>
    </Container>
  );
};

export default Recommendations;