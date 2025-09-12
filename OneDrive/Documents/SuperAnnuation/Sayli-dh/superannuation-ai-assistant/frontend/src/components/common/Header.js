// components/common/Header.js
import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Avatar,
  Box,
  Chip
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountCircle as AccountIcon,
} from '@mui/icons-material';

const Header = ({ onMenuClick, userProfile }) => {
  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          onClick={onMenuClick}
          edge="start"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          SuperAI Assistant
        </Typography>
        
        {userProfile && (
          <Box display="flex" alignItems="center" gap={1}>
            <Chip 
              label={`Age ${userProfile.age}`}
              size="small"
              color="secondary"
            />
            <Avatar sx={{ width: 32, height: 32 }}>
              <AccountIcon />
            </Avatar>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;



