/**
 * Dashboard Page - Main overview for employees
 */
import { useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Button,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Assignment as TaskIcon,
  CheckCircle as CompletedIcon,
  TrendingUp as TrendingIcon,
  Psychology as AIIcon,
  Refresh as RefreshIcon,
  Star as StarIcon,
} from '@mui/icons-material';
import TaskCard from '../components/TaskCard';
import BurnoutAlert from '../components/BurnoutAlert';
import { Task } from '../types/Task';
import { BurnoutRiskResponse, Achievement } from '../types/Analytics';

// Mock data - Replace with actual API calls
const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Implement user authentication system',
    description: 'Create a secure authentication flow with JWT tokens and OAuth integration',
    assigned_to: 'user-1',
    created_by: 'manager-1',
    urgency: 5,
    deadline: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    estimated_effort: 8,
    status: 'in_progress' as any,
    priority_score: 0.92,
    dependencies: [],
    source: 'manual' as any,
    completed_at: undefined,
    actual_effort: undefined,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '2',
    title: 'Review code for payment module',
    description: 'Perform security audit and code review',
    assigned_to: 'user-1',
    created_by: 'manager-1',
    urgency: 4,
    deadline: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    estimated_effort: 4,
    status: 'pending' as any,
    priority_score: 0.75,
    dependencies: [],
    source: 'email' as any,
    completed_at: undefined,
    actual_effort: undefined,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '3',
    title: 'Update documentation for API endpoints',
    description: 'Add comprehensive documentation for new REST API endpoints',
    assigned_to: 'user-1',
    created_by: 'manager-1',
    urgency: 2,
    estimated_effort: 3,
    status: 'pending' as any,
    priority_score: 0.45,
    dependencies: [],
    source: 'manual' as any,
    completed_at: undefined,
    actual_effort: undefined,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

const mockBurnoutData: BurnoutRiskResponse = {
  employee_id: 'user-1',
  current_risk_score: 0.35,
  risk_level: 'low',
  factors: {
    overwork: 0.2,
    cognitive_overload: 0.4,
    social_isolation: 0.3,
  },
  recommendations: [
    'Keep up the good work! Maintain current work-life balance.',
    'Consider scheduling more team interactions.',
  ],
  trend: 'stable',
};

const mockAchievements: Achievement[] = [
  {
    id: '1',
    employee_id: 'user-1',
    type: 'deliverable' as any,
    description: 'Completed high-priority authentication module ahead of schedule',
    impact_score: 0.9,
    recognized_by_manager: true,
    recognition_note: 'Excellent work on the authentication system!',
    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '2',
    employee_id: 'user-1',
    type: 'innovation' as any,
    description: 'Implemented efficient caching strategy that improved performance by 40%',
    impact_score: 0.85,
    recognized_by_manager: false,
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

export default function Dashboard() {
  const [tasks] = useState<Task[]>(mockTasks);
  const [burnoutData] = useState<BurnoutRiskResponse>(mockBurnoutData);
  const [achievements] = useState<Achievement[]>(mockAchievements);
  const [loading, setLoading] = useState(false);

  const prioritizedTasks = [...tasks].sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
  const activeTasks = tasks.filter(t => t.status !== 'completed' && t.status !== 'cancelled');
  const completedToday = 5; // Mock value
  const workload = tasks.reduce((sum, t) => sum + (t.estimated_effort || 0) * (t.priority_score || 0), 0);

  const handleRefresh = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => setLoading(false), 1000);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Welcome back, John! 👋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's your performance overview
          </Typography>
        </Box>
        <IconButton onClick={handleRefresh} disabled={loading}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                    Active Tasks
                  </Typography>
                  <Typography variant="h3" fontWeight={700}>
                    {activeTasks.length}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.3)', width: 56, height: 56 }}>
                  <TaskIcon sx={{ fontSize: 32 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                    Completed Today
                  </Typography>
                  <Typography variant="h3" fontWeight={700}>
                    {completedToday}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.3)', width: 56, height: 56 }}>
                  <CompletedIcon sx={{ fontSize: 32 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              color: 'white',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                    Workload Score
                  </Typography>
                  <Typography variant="h3" fontWeight={700}>
                    {workload.toFixed(1)}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.3)', width: 56, height: 56 }}>
                  <TrendingIcon sx={{ fontSize: 32 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
              color: 'white',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                    AI Score
                  </Typography>
                  <Typography variant="h3" fontWeight={700}>
                    {(mockBurnoutData.current_risk_score * 100).toFixed(0)}%
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.3)', width: 56, height: 56 }}>
                  <AIIcon sx={{ fontSize: 32 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {/* Burnout Alert */}
          <BurnoutAlert burnoutData={burnoutData} />

          {/* Priority Tasks */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" fontWeight={700}>
                  🎯 Priority Tasks
                </Typography>
                <Button variant="contained" size="small">
                  View All
                </Button>
              </Box>
              {prioritizedTasks.slice(0, 3).map(task => (
                <TaskCard key={task.id} task={task} />
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          {/* Recent Achievements */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                🏆 Recent Achievements
              </Typography>
              {achievements.map(achievement => (
                <Box
                  key={achievement.id}
                  sx={{
                    p: 2,
                    mb: 2,
                    borderRadius: 2,
                    background: achievement.recognized_by_manager
                      ? 'linear-gradient(135deg, #FFF9C4 0%, #FFF59D 100%)'
                      : '#f5f5f5',
                    border: achievement.recognized_by_manager ? '2px solid #FBC02D' : 'none',
                  }}
                >
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <StarIcon sx={{ color: achievement.recognized_by_manager ? '#F57F17' : '#9E9E9E' }} />
                    <Typography variant="body2" fontWeight={600}>
                      {achievement.description}
                    </Typography>
                  </Box>
                  {achievement.recognized_by_manager && achievement.recognition_note && (
                    <Typography variant="caption" sx={{ fontStyle: 'italic', color: '#F57F17' }}>
                      "{achievement.recognition_note}"
                    </Typography>
                  )}
                  <Box sx={{ mt: 1 }}>
                    <Chip
                      label={`Impact: ${(achievement.impact_score * 100).toFixed(0)}%`}
                      size="small"
                      sx={{ fontSize: '0.7rem' }}
                    />
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                ⚡ Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button variant="outlined" fullWidth>
                  Create New Task
                </Button>
                <Button variant="outlined" fullWidth>
                  Request Time Off
                </Button>
                <Button variant="outlined" fullWidth>
                  Schedule Meeting
                </Button>
                <Button variant="outlined" fullWidth>
                  View Team Calendar
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
