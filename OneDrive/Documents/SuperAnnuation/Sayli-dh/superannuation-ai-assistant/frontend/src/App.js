import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, CircularProgress, Typography } from '@mui/material';
import { Toaster } from 'react-hot-toast';

// Components
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';

// Pages  
import Profile from './pages/Profile';
import Recommendations from './pages/Recommendations';

// Styles
import './App.css';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    success: {
      main: '#2e7d32',
    },
    warning: {
      main: '#ed6c02',
    },
    error: {
      main: '#d32f2f',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      marginBottom: '1rem',
    },
    h5: {
      fontWeight: 500,
      marginBottom: '0.8rem',
    },
    body1: {
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          padding: '8px 24px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
  },
});

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Box
            display="flex"
            flexDirection="column"
            justifyContent="center"
            alignItems="center"
            minHeight="100vh"
            gap={2}
          >
            <Typography variant="h5" color="error">
              Something went wrong
            </Typography>
            <Typography variant="body1" color="textSecondary">
              {this.state.error?.message || 'An unexpected error occurred'}
            </Typography>
            <button 
              onClick={() => window.location.reload()}
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '8px',
                backgroundColor: '#1976d2',
                color: 'white',
                cursor: 'pointer'
              }}
            >
              Reload Page
            </button>
          </Box>
        </ThemeProvider>
      );
    }

    return this.props.children;
  }
}

// Loading Component
const LoadingScreen = () => (
  <Box
    display="flex"
    flexDirection="column"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
    gap={2}
  >
    <CircularProgress size={60} />
    <Typography variant="h6" color="textSecondary">
      Loading Superannuation AI Assistant...
    </Typography>
  </Box>
);

function App() {
  const [userProfile, setUserProfile] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setError(null);
      
      // Try to load from localStorage first
      const savedProfile = localStorage.getItem('userProfile');
      if (savedProfile) {
        const profile = JSON.parse(savedProfile);
        setUserProfile(profile);
        console.log('Loaded user profile from localStorage:', profile);
      } else {
        console.log('No saved profile found, user will need to create one');
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      setError('Failed to load user profile');
      // Clear potentially corrupted data
      localStorage.removeItem('userProfile');
    } finally {
      setLoading(false);
    }
  };

  const updateUserProfile = (profile) => {
    try {
      setUserProfile(profile);
      localStorage.setItem('userProfile', JSON.stringify(profile));
      console.log('Updated user profile:', profile);
    } catch (error) {
      console.error('Error saving user profile:', error);
      setError('Failed to save user profile');
    }
  };

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LoadingScreen />
      </ThemeProvider>
    );
  }

  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <div className="App">
            <Header 
              onMenuClick={handleSidebarToggle}
              userProfile={userProfile}
            />
            
            <Box display="flex" minHeight="calc(100vh - 64px)" sx={{ pt: 8 }}>
              <Sidebar 
                open={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
                userProfile={userProfile}
              />
              
              <Box
                component="main"
                flexGrow={1}
                sx={{ p: 3 }}
              >
                <Routes>
                  <Route 
                    path="/" 
                    element={
                      <Dashboard 
                        userProfile={userProfile}
                        error={error}
                      />
                    } 
                  />
                  <Route 
                    path="/dashboard" 
                    element={
                      <Dashboard 
                        userProfile={userProfile}
                        error={error}
                      />
                    } 
                  />
                  <Route 
                    path="/chat" 
                    element={
                      <ChatInterface 
                        userProfile={userProfile}
                      />
                    } 
                  />
                  <Route 
                    path="/profile" 
                    element={
                      <Profile 
                        userProfile={userProfile}
                        onUpdateProfile={updateUserProfile}
                        error={error}
                        setError={setError}
                      />
                    } 
                  />
                  <Route 
                    path="/recommendations" 
                    element={
                      <Recommendations 
                        userProfile={userProfile}
                      />
                    } 
                  />
                  {/* Fallback route */}
                  <Route 
                    path="*" 
                    element={
                      <Box textAlign="center" py={4}>
                        <Typography variant="h5" gutterBottom>
                          Page Not Found
                        </Typography>
                        <Typography variant="body1" color="textSecondary">
                          The page you're looking for doesn't exist.
                        </Typography>
                      </Box>
                    } 
                  />
                </Routes>
              </Box>
            </Box>
          </div>
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                style: {
                  background: '#2e7d32',
                },
              },
              error: {
                duration: 5000,
                style: {
                  background: '#d32f2f',
                },
              },
            }}
          />
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;