import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import UserProfile from '../components/UserProfile';

const Profile = ({ userProfile, onUpdateProfile }) => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Your Profile
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Manage your personal and financial information to get personalized investment recommendations.
        </Typography>
        
        <UserProfile 
          userProfile={userProfile}
          onProfileUpdate={onUpdateProfile} 
        />
      </Box>
    </Container>
  );
};

export default Profile;