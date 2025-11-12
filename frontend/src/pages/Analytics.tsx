/**
 * Analytics Page - Burnout metrics and performance analytics
 */
import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import BurnoutAlert from '../components/BurnoutAlert';
import { BurnoutRiskResponse } from '../types/Analytics';

const mockBurnoutData: BurnoutRiskResponse = {
  employee_id: 'user-1',
  current_risk_score: 0.35,
  risk_level: 'low',
  factors: {
    overwork: 0.2,
    cognitive_overload: 0.4,
    social_isolation: 0.3,
    poor_completion: 0.15,
  },
  recommendations: [
    'Keep up the good work! Maintain current work-life balance.',
    'Consider scheduling more team interactions.',
    'Take regular breaks to avoid cognitive fatigue.',
  ],
  trend: 'stable',
};

const burnoutTrendData = [
  { date: 'Mon', risk: 0.25, hours: 7.5, breaks: 3 },
  { date: 'Tue', risk: 0.30, hours: 8.5, breaks: 2 },
  { date: 'Wed', risk: 0.35, hours: 9.0, breaks: 2 },
  { date: 'Thu', risk: 0.32, hours: 8.0, breaks: 3 },
  { date: 'Fri', risk: 0.28, hours: 7.0, breaks: 4 },
  { date: 'Sat', risk: 0.15, hours: 0, breaks: 0 },
  { date: 'Sun', risk: 0.18, hours: 2, breaks: 1 },
];

const taskDistributionData = [
  { name: 'Completed', value: 45, color: '#4CAF50' },
  { name: 'In Progress', value: 25, color: '#2196F3' },
  { name: 'Pending', value: 20, color: '#FFC107' },
  { name: 'Blocked', value: 10, color: '#F44336' },
];

const productivityData = [
  { period: 'Morning', productivity: 85, tasks: 12 },
  { period: 'Afternoon', productivity: 70, tasks: 8 },
  { period: 'Evening', productivity: 45, tasks: 3 },
];

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('7days');

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Analytics & Insights 📊
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Track your performance and wellbeing metrics
          </Typography>
        </Box>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            label="Time Range"
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <MenuItem value="7days">Last 7 Days</MenuItem>
            <MenuItem value="30days">Last 30 Days</MenuItem>
            <MenuItem value="90days">Last 90 Days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Burnout Alert */}
      <BurnoutAlert burnoutData={mockBurnoutData} />

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Burnout Risk Trend */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Burnout Risk Trend
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Daily burnout risk score and work patterns
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={burnoutTrendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e0e0e0',
                      borderRadius: 8,
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="risk"
                    stroke="#F44336"
                    strokeWidth={3}
                    name="Risk Score"
                    dot={{ fill: '#F44336', r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="hours"
                    stroke="#2196F3"
                    strokeWidth={2}
                    name="Hours Worked"
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Task Distribution */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Task Distribution
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Current task status breakdown
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={taskDistributionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {taskDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Productivity Patterns */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Productivity Patterns
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Your performance during different times of day
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={productivityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e0e0e0',
                      borderRadius: 8,
                    }}
                  />
                  <Legend />
                  <Bar dataKey="productivity" fill="#667eea" name="Productivity %" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="tasks" fill="#764ba2" name="Tasks Completed" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Factor Breakdown */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Risk Factors Breakdown
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Contributing factors to burnout risk
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart
                  data={Object.entries(mockBurnoutData.factors).map(([key, value]) => ({
                    factor: key.replace(/_/g, ' '),
                    value: value * 100,
                  }))}
                  layout="vertical"
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis dataKey="factor" type="category" width={150} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e0e0e0',
                      borderRadius: 8,
                    }}
                  />
                  <Bar dataKey="value" fill="#FF9800" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
