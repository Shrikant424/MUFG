import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const UserProfile = ({ onProfileUpdate }) => {
  const [profile, setProfile] = useState({
    age: '',
    gender: 'Male',
    country: 'Australia',
    employmentStatus: 'Full-time',
    annualIncome: '',
    currentSavings: '',
    retirementAgeGoal: 65,
    riskTolerance: 'Medium',
    maritalStatus: 'Single',
    numberOfDependents: 0,
    educationLevel: 'Bachelor\'s',
    healthStatus: 'Good',
    homeOwnershipStatus: 'Own',
    monthlyExpenses: '',
    financialGoals: 'Retirement',
    investmentExperience: 'Intermediate'
  });

  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const savedProfile = localStorage.getItem('userProfile');
      if (savedProfile) {
        const parsedProfile = JSON.parse(savedProfile);
        setProfile(parsedProfile);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      // Validate required fields
      if (!profile.age || !profile.annualIncome) {
        throw new Error('Age and Annual Income are required');
      }

      // Save to localStorage
      localStorage.setItem('userProfile', JSON.stringify(profile));
      
      // Notify parent component
      if (onProfileUpdate) {
        onProfileUpdate(profile);
      }

      setMessage('Profile updated successfully!');
      setIsEditing(false);
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const calculateYearsToRetirement = () => {
    if (profile.age && profile.retirementAgeGoal) {
      return Math.max(0, profile.retirementAgeGoal - profile.age);
    }
    return 0;
  };

  const calculateSavingsRate = () => {
    if (profile.annualIncome && profile.monthlyExpenses) {
      const annualExpenses = profile.monthlyExpenses * 12;
      const annualSavings = profile.annualIncome - annualExpenses;
      return Math.max(0, (annualSavings / profile.annualIncome * 100)).toFixed(1);
    }
    return 0;
  };

  if (!isEditing) {
    return (
      <div className="user-profile-display">
        <div className="profile-header">
          <h2>Your Profile</h2>
          <button 
            className="edit-button"
            onClick={() => setIsEditing(true)}
          >
            Edit Profile
          </button>
        </div>
        
        <div className="profile-summary">
          <div className="profile-card">
            <h3>Personal Information</h3>
            <div className="profile-grid">
              <div className="profile-item">
                <label>Age:</label>
                <span>{profile.age || 'Not set'}</span>
              </div>
              <div className="profile-item">
                <label>Gender:</label>
                <span>{profile.gender}</span>
              </div>
              <div className="profile-item">
                <label>Country:</label>
                <span>{profile.country}</span>
              </div>
              <div className="profile-item">
                <label>Marital Status:</label>
                <span>{profile.maritalStatus}</span>
              </div>
            </div>
          </div>

          <div className="profile-card">
            <h3>Financial Information</h3>
            <div className="profile-grid">
              <div className="profile-item">
                <label>Annual Income:</label>
                <span>${profile.annualIncome?.toLocaleString() || 'Not set'}</span>
              </div>
              <div className="profile-item">
                <label>Current Savings:</label>
                <span>${profile.currentSavings?.toLocaleString() || 'Not set'}</span>
              </div>
              <div className="profile-item">
                <label>Monthly Expenses:</label>
                <span>${profile.monthlyExpenses?.toLocaleString() || 'Not set'}</span>
              </div>
              <div className="profile-item">
                <label>Savings Rate:</label>
                <span>{calculateSavingsRate()}%</span>
              </div>
            </div>
          </div>

          <div className="profile-card">
            <h3>Retirement Planning</h3>
            <div className="profile-grid">
              <div className="profile-item">
                <label>Retirement Age Goal:</label>
                <span>{profile.retirementAgeGoal}</span>
              </div>
              <div className="profile-item">
                <label>Years to Retirement:</label>
                <span>{calculateYearsToRetirement()}</span>
              </div>
              <div className="profile-item">
                <label>Risk Tolerance:</label>
                <span>{profile.riskTolerance}</span>
              </div>
              <div className="profile-item">
                <label>Investment Experience:</label>
                <span>{profile.investmentExperience}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-profile-form">
      <div className="form-header">
        <h2>Edit Your Profile</h2>
        <button 
          className="cancel-button"
          onClick={() => {
            setIsEditing(false);
            loadProfile(); // Reset changes
          }}
        >
          Cancel
        </button>
      </div>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="profile-form">
        <div className="form-section">
          <h3>Personal Information</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="age">Age *</label>
              <input
                type="number"
                id="age"
                name="age"
                value={profile.age}
                onChange={handleInputChange}
                min="18"
                max="100"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="gender">Gender</label>
              <select
                id="gender"
                name="gender"
                value={profile.gender}
                onChange={handleInputChange}
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="country">Country</label>
              <select
                id="country"
                name="country"
                value={profile.country}
                onChange={handleInputChange}
              >
                <option value="Australia">Australia</option>
                <option value="Canada">Canada</option>
                <option value="UK">UK</option>
                <option value="USA">USA</option>
                <option value="Germany">Germany</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="maritalStatus">Marital Status</label>
              <select
                id="maritalStatus"
                name="maritalStatus"
                value={profile.maritalStatus}
                onChange={handleInputChange}
              >
                <option value="Single">Single</option>
                <option value="Married">Married</option>
                <option value="Divorced">Divorced</option>
                <option value="Widowed">Widowed</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Employment & Finance</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="employmentStatus">Employment Status</label>
              <select
                id="employmentStatus"
                name="employmentStatus"
                value={profile.employmentStatus}
                onChange={handleInputChange}
              >
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Self-employed">Self-employed</option>
                <option value="Unemployed">Unemployed</option>
                <option value="Retired">Retired</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="annualIncome">Annual Income ($) *</label>
              <input
                type="number"
                id="annualIncome"
                name="annualIncome"
                value={profile.annualIncome}
                onChange={handleInputChange}
                min="0"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="currentSavings">Current Savings ($)</label>
              <input
                type="number"
                id="currentSavings"
                name="currentSavings"
                value={profile.currentSavings}
                onChange={handleInputChange}
                min="0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="monthlyExpenses">Monthly Expenses ($)</label>
              <input
                type="number"
                id="monthlyExpenses"
                name="monthlyExpenses"
                value={profile.monthlyExpenses}
                onChange={handleInputChange}
                min="0"
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Retirement Planning</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="retirementAgeGoal">Retirement Age Goal</label>
              <input
                type="number"
                id="retirementAgeGoal"
                name="retirementAgeGoal"
                value={profile.retirementAgeGoal}
                onChange={handleInputChange}
                min="50"
                max="80"
              />
            </div>

            <div className="form-group">
              <label htmlFor="riskTolerance">Risk Tolerance</label>
              <select
                id="riskTolerance"
                name="riskTolerance"
                value={profile.riskTolerance}
                onChange={handleInputChange}
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="investmentExperience">Investment Experience</label>
              <select
                id="investmentExperience"
                name="investmentExperience"
                value={profile.investmentExperience}
                onChange={handleInputChange}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Expert">Expert</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="financialGoals">Primary Financial Goal</label>
              <select
                id="financialGoals"
                name="financialGoals"
                value={profile.financialGoals}
                onChange={handleInputChange}
              >
                <option value="Retirement">Retirement</option>
                <option value="Home Purchase">Home Purchase</option>
                <option value="Education">Education</option>
                <option value="Travel">Travel</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Legacy Planning">Legacy Planning</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="save-button">
            {loading ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default UserProfile;