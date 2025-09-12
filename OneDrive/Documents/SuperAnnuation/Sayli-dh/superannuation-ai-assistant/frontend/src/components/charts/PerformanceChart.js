import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { Box, Typography, ToggleButton, ToggleButtonGroup, Chip } from '@mui/material';

const PerformanceChart = ({ userProfile }) => {
  const [chartData, setChartData] = useState([]);
  const [viewType, setViewType] = useState('balance');

  useEffect(() => {
    if (userProfile) {
      generateProjectionData();
    }
  }, [userProfile, viewType]);

  const generateProjectionData = () => {
    const currentAge = userProfile.age || 35;
    const retirementAge = userProfile.retirement_age_goal || 65;
    const currentBalance = userProfile.current_savings || 50000;
    const annualIncome = userProfile.annual_income || 70000;
    const riskTolerance = userProfile.risk_tolerance || 'Medium';

    // Expected returns based on risk tolerance
    const expectedReturns = {
      'Low': 0.05,
      'Medium': 0.07,
      'High': 0.09
    };

    const expectedReturn = expectedReturns[riskTolerance] || 0.07;
    const employerContribution = annualIncome * 0.11; // 11% super guarantee

    const data = [];
    let balance = currentBalance;
    let pessimisticBalance = currentBalance;
    let optimisticBalance = currentBalance;

    for (let age = currentAge; age <= Math.min(retirementAge + 5, 85); age++) {
      const year = new Date().getFullYear() + (age - currentAge);
      
      // Calculate different scenarios
      if (age < retirementAge) {
        // Accumulation phase
        balance = balance * (1 + expectedReturn) + employerContribution;
        pessimisticBalance = pessimisticBalance * (1 + expectedReturn * 0.6) + employerContribution;
        optimisticBalance = optimisticBalance * (1 + expectedReturn * 1.4) + employerContribution;
      } else {
        // Retirement phase - 4% withdrawal rule
        const withdrawalRate = 0.04;
        balance = Math.max(0, balance * (1 + expectedReturn - withdrawalRate));
        pessimisticBalance = Math.max(0, pessimisticBalance * (1 + expectedReturn * 0.6 - withdrawalRate));
        optimisticBalance = Math.max(0, optimisticBalance * (1 + expectedReturn * 1.4 - withdrawalRate));
      }

      const annualIncome = balance * 0.04; // 4% withdrawal rule
      const monthlyIncome = annualIncome / 12;

      data.push({
        age,
        year,
        balance: Math.round(balance),
        pessimisticBalance: Math.round(pessimisticBalance),
        optimisticBalance: Math.round(optimisticBalance),
        annualIncome: Math.round(annualIncome),
        monthlyIncome: Math.round(monthlyIncome),
        phase: age < retirementAge ? 'Accumulation' : 'Retirement'
      });
    }

    setChartData(data);
  };

  const formatCurrency = (value) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toLocaleString()}`;
  };

  const handleViewChange = (event, newView) => {
    if (newView !== null) {
      setViewType(newView);
    }
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Box
          sx={{
            backgroundColor: 'white',
            p: 2,
            border: '1px solid #ccc',
            borderRadius: 1,
            boxShadow: 2
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            Age {label} • {data.year} • {data.phase} Phase
          </Typography>
          {viewType === 'balance' && (
            <>
              <Typography variant="body2" color="primary">
                Expected: {formatCurrency(data.balance)}
              </Typography>
              <Typography variant="body2" color="error">
                Conservative: {formatCurrency(data.pessimisticBalance)}
              </Typography>
              <Typography variant="body2" color="success">
                Optimistic: {formatCurrency(data.optimisticBalance)}
              </Typography>
            </>
          )}
          {viewType === 'income' && (
            <>
              <Typography variant="body2" color="primary">
                Annual Income: {formatCurrency(data.annualIncome)}
              </Typography>
              <Typography variant="body2" color="secondary">
                Monthly Income: {formatCurrency(data.monthlyIncome)}
              </Typography>
            </>
          )}
        </Box>
      );
    }
    return null;
  };

  const retirementAge = userProfile?.retirement_age_goal || 65;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          Projection to Age 85
        </Typography>
        <ToggleButtonGroup
          value={viewType}
          exclusive
          onChange={handleViewChange}
          size="small"
        >
          <ToggleButton value="balance">
            Balance
          </ToggleButton>
          <ToggleButton value="income">
            Income
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Box mb={2}>
        <Chip
          size="small"
          label={`Retirement at age ${retirementAge}`}
          color="primary"
          variant="outlined"
        />
      </Box>

      <ResponsiveContainer width="100%" height={400}>
        {viewType === 'balance' ? (
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="age" 
              domain={['dataMin', 'dataMax']}
            />
            <YAxis 
              tickFormatter={formatCurrency}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Retirement line */}
            <defs>
              <linearGradient id="retirementLine" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff5722" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ff5722" stopOpacity={0}/>
              </linearGradient>
            </defs>

            <Area
              type="monotone"
              dataKey="optimisticBalance"
              stackId="1"
              stroke="#4caf50"
              fill="#4caf50"
              fillOpacity={0.1}
              name="Optimistic Scenario"
            />
            <Area
              type="monotone"
              dataKey="balance"
              stackId="2"
              stroke="#1976d2"
              fill="#1976d2"
              fillOpacity={0.2}
              name="Expected Scenario"
            />
            <Area
              type="monotone"
              dataKey="pessimisticBalance"
              stackId="3"
              stroke="#f44336"
              fill="#f44336"
              fillOpacity={0.1}
              name="Conservative Scenario"
            />

            {/* Add vertical line at retirement age */}
            <Line
              type="monotone"
              dataKey={() => null}
              stroke="#ff5722"
              strokeDasharray="5 5"
              strokeWidth={2}
              dot={false}
              name="Retirement Age"
            />
          </AreaChart>
        ) : (
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="age" />
            <YAxis tickFormatter={formatCurrency} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            <Line
              type="monotone"
              dataKey="annualIncome"
              stroke="#1976d2"
              strokeWidth={3}
              name="Annual Retirement Income"
            />
            <Line
              type="monotone"
              dataKey="monthlyIncome"
              stroke="#dc004e"
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Monthly Retirement Income"
            />
          </LineChart>
        )}
      </ResponsiveContainer>

      <Box mt={2}>
        <Typography variant="body2" color="text.secondary">
          <strong>Assumptions:</strong> {' '}
          11% employer super contributions until retirement, 4% withdrawal rate in retirement, 
          {userProfile?.risk_tolerance === 'High' ? ' 9%' : userProfile?.risk_tolerance === 'Low' ? ' 5%' : ' 7%'} expected annual return
          based on your {userProfile?.risk_tolerance || 'Medium'} risk tolerance.
        </Typography>
      </Box>
    </Box>
  );
};

export default PerformanceChart;