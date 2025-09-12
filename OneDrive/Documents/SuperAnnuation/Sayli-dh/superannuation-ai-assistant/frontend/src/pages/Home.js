import React, { useState, useEffect } from 'react';
import Dashboard from '../forms/Dashboard';
import UserProfile from '../components/UserProfile';
import InvestmentRecommendations from '../forms/InvestmentRecommendations';
import ChatInterface from '../forms/ChatInterface';

const Home = () => {
  const [userProfile, setUserProfile] = useState(null);
  const [activeView, setActiveView] = useState('dashboard');
  const [isProfileComplete, setIsProfileComplete] = useState(false);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = () => {
    try {
      const savedProfile = localStorage.getItem('userProfile');
      if (savedProfile) {
        const profile = JSON.parse(savedProfile);
        setUserProfile(profile);
        checkProfileCompleteness(profile);
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
  };

  const checkProfileCompleteness = (profile) => {
    const requiredFields = ['age', 'annualIncome', 'riskTolerance'];
    const complete = requiredFields.every(field => 
      profile[field] !== undefined && profile[field] !== '' && profile[field] !== null
    );
    setIsProfileComplete(complete);
  };

  const handleProfileUpdate = (newProfile) => {
    setUserProfile(newProfile);
    checkProfileCompleteness(newProfile);
  };

  const renderActiveView = () => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard userProfile={userProfile} />;
      case 'profile':
        return <UserProfile onProfileUpdate={handleProfileUpdate} />;
      case 'recommendations':
        return <InvestmentRecommendations userProfile={userProfile} />;
      case 'chat':
        return <ChatInterface userProfile={userProfile} />;
      default:
        return <Dashboard userProfile={userProfile} />;
    }
  };

  return (
    <div className="home-container">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1>SuperAI Assistant</h1>
            <p>Your AI-Powered Superannuation Advisor</p>
          </div>
          
          <nav className="main-navigation">
            <button 
              className={activeView === 'dashboard' ? 'nav-button active' : 'nav-button'}
              onClick={() => setActiveView('dashboard')}
            >
              📊 Dashboard
            </button>
            <button 
              className={activeView === 'profile' ? 'nav-button active' : 'nav-button'}
              onClick={() => setActiveView('profile')}
            >
              👤 Profile
            </button>
            <button 
              className={activeView === 'recommendations' ? 'nav-button active' : 'nav-button'}
              onClick={() => setActiveView('recommendations')}
              disabled={!isProfileComplete}
            >
              💡 Recommendations
            </button>
            <button 
              className={activeView === 'chat' ? 'nav-button active' : 'nav-button'}
              onClick={() => setActiveView('chat')}
            >
              💬 AI Chat
            </button>
          </nav>
        </div>
      </header>

      {!isProfileComplete && (
        <div className="profile-incomplete-banner">
          <div className="banner-content">
            <span className="banner-icon">⚠️</span>
            <div className="banner-text">
              <strong>Complete your profile to get personalized recommendations</strong>
              <p>Fill out your age, income, and risk tolerance to unlock AI-powered investment advice.</p>
            </div>
            <button 
              className="complete-profile-button"
              onClick={() => setActiveView('profile')}
            >
              Complete Profile
            </button>
          </div>
        </div>
      )}

      <main className="main-content">
        {renderActiveView()}
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>About SuperAI Assistant</h4>
            <p>AI-powered superannuation advice tailored to your financial goals and retirement timeline.</p>
          </div>
          <div className="footer-section">
            <h4>Features</h4>
            <ul>
              <li>Personalized investment recommendations</li>
              <li>Risk assessment and portfolio analysis</li>
              <li>Retirement planning projections</li>
              <li>Interactive AI chat support</li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Disclaimer</h4>
            <p>This tool provides educational information only. Consult with a licensed financial advisor for professional advice.</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 SuperAI Assistant. Built for the Superannuation AI Hackathon.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;