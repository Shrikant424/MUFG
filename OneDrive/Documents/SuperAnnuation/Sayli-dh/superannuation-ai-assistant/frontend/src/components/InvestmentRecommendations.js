import React, { useState, useEffect } from 'react';
import api from '../services/api';
import PerformanceChart from './charts/PerformanceChart';

const InvestmentRecommendations = ({ userProfile }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTab, setSelectedTab] = useState('recommendations');

  useEffect(() => {
    if (userProfile && userProfile.age && userProfile.annualIncome) {
      loadRecommendations();
    }
  }, [userProfile]);

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.getRecommendations(userProfile);
      setRecommendations(response);
    } catch (err) {
      setError('Failed to load recommendations. Please try again.');
      console.error('Error loading recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(0)}K`;
    } else {
      return `${amount?.toFixed(0) || 0}`;
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Low': return '#4CAF50';
      case 'Medium': return '#FF9800';
      case 'High': return '#f44336';
      default: return '#757575';
    }
  };

  const getPerformanceColor = (performance) => {
    if (performance >= 8) return '#4CAF50';
    if (performance >= 6) return '#FF9800';
    return '#f44336';
  };

  if (!userProfile || !userProfile.age || !userProfile.annualIncome) {
    return (
      <div className="recommendations-container">
        <div className="empty-state">
          <h3>Complete Your Profile First</h3>
          <p>Please fill out your profile information to get personalized investment recommendations.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="recommendations-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Analyzing your profile and generating recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="recommendations-container">
        <div className="error-state">
          <h3>Error Loading Recommendations</h3>
          <p>{error}</p>
          <button onClick={loadRecommendations} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!recommendations) {
    return (
      <div className="recommendations-container">
        <div className="empty-state">
          <h3>No Recommendations Available</h3>
          <p>Unable to generate recommendations at this time.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recommendations-container">
      <div className="recommendations-header">
        <h2>Your Personalized Investment Recommendations</h2>
        <div className="recommendation-tabs">
          <button 
            className={selectedTab === 'recommendations' ? 'active' : ''}
            onClick={() => setSelectedTab('recommendations')}
          >
            Recommendations
          </button>
          <button 
            className={selectedTab === 'allocation' ? 'active' : ''}
            onClick={() => setSelectedTab('allocation')}
          >
            Asset Allocation
          </button>
          <button 
            className={selectedTab === 'projections' ? 'active' : ''}
            onClick={() => setSelectedTab('projections')}
          >
            Projections
          </button>
        </div>
      </div>

      {selectedTab === 'recommendations' && (
        <div className="recommendations-content">
          {/* Profile Summary */}
          <div className="profile-summary-card">
            <h3>Your Investment Profile</h3>
            <div className="profile-stats">
              <div className="stat">
                <label>Risk Tolerance</label>
                <span style={{ color: getRiskColor(userProfile.riskTolerance) }}>
                  {userProfile.riskTolerance}
                </span>
              </div>
              <div className="stat">
                <label>Time Horizon</label>
                <span>{(userProfile.retirementAgeGoal || 65) - (userProfile.age || 30)} years</span>
              </div>
              <div className="stat">
                <label>Investment Experience</label>
                <span>{userProfile.investmentExperience || 'Intermediate'}</span>
              </div>
            </div>
          </div>

          {/* Top Recommendations */}
          {recommendations.top_funds && (
            <div className="top-recommendations">
              <h3>Top Fund Recommendations</h3>
              <div className="funds-grid">
                {recommendations.top_funds.map((fund, index) => (
                  <div key={index} className="fund-card">
                    <div className="fund-header">
                      <h4>{fund.fund_name}</h4>
                      <div className="fund-rating">
                        <span className="rating-label">Rating:</span>
                        <span className={`rating ${fund.rating?.toLowerCase()}`}>
                          {fund.rating}
                        </span>
                      </div>
                    </div>
                    <div className="fund-metrics">
                      <div className="metric">
                        <label>Expected Return</label>
                        <span style={{ color: getPerformanceColor(fund.annual_return) }}>
                          {fund.annual_return?.toFixed(2)}%
                        </span>
                      </div>
                      <div className="metric">
                        <label>Volatility</label>
                        <span>{fund.volatility?.toFixed(2)}%</span>
                      </div>
                      <div className="metric">
                        <label>Fees</label>
                        <span>{fund.fees?.toFixed(2)}%</span>
                      </div>
                      <div className="metric">
                        <label>Investment Type</label>
                        <span>{fund.investment_type}</span>
                      </div>
                    </div>
                    <div className="fund-description">
                      <p>Net Return: <strong>{fund.net_return?.toFixed(2)}%</strong></p>
                      <p>Sharpe Ratio: <strong>{fund.sharpe_ratio?.toFixed(2)}</strong></p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Investment Insights */}
          {recommendations.insights && (
            <div className="insights-section">
              <h3>Key Insights</h3>
              <div className="insights-list">
                {recommendations.insights.map((insight, index) => (
                  <div key={index} className="insight-card">
                    <div className="insight-icon">💡</div>
                    <p>{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Items */}
          {recommendations.action_items && (
            <div className="action-items">
              <h3>Recommended Actions</h3>
              <div className="actions-list">
                {recommendations.action_items.map((action, index) => (
                  <div key={index} className="action-item">
                    <div className="action-priority">
                      <span className={`priority ${action.priority?.toLowerCase()}`}>
                        {action.priority}
                      </span>
                    </div>
                    <div className="action-content">
                      <h4>{action.title}</h4>
                      <p>{action.description}</p>
                      {action.timeline && (
                        <span className="timeline">Timeline: {action.timeline}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {selectedTab === 'allocation' && (
        <div className="allocation-content">
          {recommendations.recommended_allocation && (
            <div className="allocation-section">
              <h3>Recommended Asset Allocation</h3>
              <div className="allocation-visual">
                <div className="allocation-chart">
                  {Object.entries(recommendations.recommended_allocation).map(([asset, percentage]) => (
                    <div 
                      key={asset}
                      className="allocation-bar"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: getAssetColor(asset)
                      }}
                    >
                      <span className="allocation-label">
                        {asset}: {percentage}%
                      </span>
                    </div>
                  ))}
                </div>
                <div className="allocation-legend">
                  {Object.entries(recommendations.recommended_allocation).map(([asset, percentage]) => (
                    <div key={asset} className="legend-item">
                      <div 
                        className="legend-color"
                        style={{ backgroundColor: getAssetColor(asset) }}
                      ></div>
                      <span>{asset}: {percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="allocation-explanation">
                <h4>Why This Allocation?</h4>
                <p>Based on your {userProfile.riskTolerance?.toLowerCase()} risk tolerance and {(userProfile.retirementAgeGoal || 65) - (userProfile.age || 30)} years until retirement, this allocation balances growth potential with risk management.</p>
              </div>
            </div>
          )}
        </div>
      )}

      {selectedTab === 'projections' && (
        <div className="projections-content">
          {recommendations.retirement_projection && (
            <div className="projections-section">
              <h3>Retirement Projections</h3>
              <div className="projection-cards">
                <div className="projection-card">
                  <h4>Projected Retirement Balance</h4>
                  <div className="projection-value">
                    {formatCurrency(recommendations.retirement_projection.projected_balance)}
                  </div>
                  <p>At age {userProfile.retirementAgeGoal || 65}</p>
                </div>
                
                <div className="projection-card">
                  <h4>Monthly Income in Retirement</h4>
                  <div className="projection-value">
                    {formatCurrency(recommendations.retirement_projection.monthly_income)}
                  </div>
                  <p>Based on 4% withdrawal rule</p>
                </div>
                
                <div className="projection-card">
                  <h4>Recommended Monthly Contribution</h4>
                  <div className="projection-value">
                    {formatCurrency(recommendations.retirement_projection.recommended_contribution)}
                  </div>
                  <p>To meet retirement goals</p>
                </div>
              </div>
              
              {recommendations.retirement_projection.projection_chart_data && (
                <div className="projection-chart">
                  <h4>Growth Projection Over Time</h4>
                  <PerformanceChart 
                    data={recommendations.retirement_projection.projection_chart_data}
                    title="Projected Portfolio Value"
                  />
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="recommendations-footer">
        <p className="disclaimer">
          <strong>Disclaimer:</strong> These recommendations are based on historical data and projections. 
          Past performance does not guarantee future results. Please consult with a licensed financial advisor 
          before making investment decisions.
        </p>
        <button onClick={loadRecommendations} className="refresh-button">
          Refresh Recommendations
        </button>
      </div>
    </div>
  );

  function getAssetColor(asset) {
    const colors = {
      'Stocks': '#2196F3',
      'Bonds': '#4CAF50',
      'Real Estate': '#FF9800',
      'Cash': '#757575',
      'International': '#9C27B0',
      'Alternatives': '#607D8B'
    };
    return colors[asset] || '#757575';
  }}

  export default InvestmentRecommendations;
