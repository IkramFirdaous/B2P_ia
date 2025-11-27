/**
 * Team View Page - Manager view of team workload and equity
 */
import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Avatar,
  LinearProgress,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp as UpIcon,
  TrendingDown as DownIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  activeTasks: number;
  completedThisWeek: number;
  workloadScore: number;
  burnoutRisk: number;
  productivity: number;
}

const mockTeamMembers: TeamMember[] = [
  {
    id: '1',
    name: 'Alice Johnson',
    role: 'Senior Developer',
    avatar: 'AJ',
    activeTasks: 8,
    completedThisWeek: 12,
    workloadScore: 45.2,
    burnoutRisk: 0.25,
    productivity: 92,
  },
  {
    id: '2',
    name: 'Bob Smith',
    role: 'Full Stack Developer',
    avatar: 'BS',
    activeTasks: 12,
    completedThisWeek: 8,
    workloadScore: 68.5,
    burnoutRisk: 0.65,
    productivity: 78,
  },
  {
    id: '3',
    name: 'Carol Williams',
    role: 'Frontend Developer',
    avatar: 'CW',
    activeTasks: 6,
    completedThisWeek: 15,
    workloadScore: 32.8,
    burnoutRisk: 0.15,
    productivity: 95,
  },
  {
    id: '4',
    name: 'David Brown',
    role: 'Backend Developer',
    avatar: 'DB',
    activeTasks: 10,
    completedThisWeek: 10,
    workloadScore: 52.3,
    burnoutRisk: 0.45,
    productivity: 85,
  },
];

export default function TeamView() {
  const { user, token } = useAuth();
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTeamData();
  }, []);

  const fetchTeamData = async () => {
    if (!token || !user?.team_id) {
      setError('Vous devez faire partie d\'une équipe pour voir cette page');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Fetch team members
      const response = await axios.get(`${API_URL}/teams/${user.team_id}/members`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const members = response.data;

      // Fetch tasks and burnout data for each member
      const membersWithData = await Promise.all(
        members.map(async (member: any) => {
          try {
            // Get tasks
            const tasksRes = await axios.get(`${API_URL}/tasks`, {
              headers: { Authorization: `Bearer ${token}` },
              params: { assigned_to: member.id }
            });

            const tasks = tasksRes.data;
            const activeTasks = tasks.filter((t: any) =>
              t.status === 'pending' || t.status === 'in_progress'
            ).length;

            const completedThisWeek = tasks.filter((t: any) => {
              if (t.status !== 'completed' || !t.completed_at) return false;
              const completedDate = new Date(t.completed_at);
              const weekAgo = new Date();
              weekAgo.setDate(weekAgo.getDate() - 7);
              return completedDate >= weekAgo;
            }).length;

            // Get burnout data
            let burnoutRisk = 0.2; // default
            try {
              const burnoutRes = await axios.get(`${API_URL}/analytics/burnout/${member.id}`, {
                headers: { Authorization: `Bearer ${token}` }
              });
              burnoutRisk = burnoutRes.data.current_risk_score || 0.2;
            } catch (err) {
              console.warn(`No burnout data for ${member.name}`);
            }

            // Calculate workload score (sum of estimated efforts)
            const workloadScore = tasks
              .filter((t: any) => t.status === 'pending' || t.status === 'in_progress')
              .reduce((sum: number, t: any) => sum + (t.estimated_effort || 0), 0);

            return {
              id: member.id,
              name: member.name,
              role: member.role || 'Team Member',
              avatar: member.name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2),
              activeTasks,
              completedThisWeek,
              workloadScore,
              burnoutRisk,
              productivity: Math.max(0, Math.min(100, 100 - (burnoutRisk * 50))),
            };
          } catch (err) {
            console.error(`Error fetching data for ${member.name}:`, err);
            return null;
          }
        })
      );

      setTeamMembers(membersWithData.filter(m => m !== null) as TeamMember[]);
    } catch (err: any) {
      console.error('Failed to fetch team data:', err);
      setError(err.response?.data?.detail || 'Impossible de charger les données de l\'équipe');
      // Fallback to mock data
      setTeamMembers(mockTeamMembers);
    } finally {
      setLoading(false);
    }
  };

  const avgWorkload = teamMembers.length > 0
    ? teamMembers.reduce((sum, m) => sum + m.workloadScore, 0) / teamMembers.length
    : 0;
  const avgBurnout = teamMembers.length > 0
    ? teamMembers.reduce((sum, m) => sum + m.burnoutRisk, 0) / teamMembers.length
    : 0;
  const totalActive = teamMembers.reduce((sum, m) => sum + m.activeTasks, 0);
  const totalCompleted = teamMembers.reduce((sum, m) => sum + m.completedThisWeek, 0);

  const getRiskColor = (risk: number) => {
    if (risk >= 0.6) return '#F44336';
    if (risk >= 0.4) return '#FF9800';
    return '#4CAF50';
  };

  const getRiskLabel = (risk: number) => {
    if (risk >= 0.6) return 'High';
    if (risk >= 0.4) return 'Medium';
    return 'Low';
  };

  return (
    <Box>
      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Team Overview
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Monitor team workload and wellbeing
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
            onClick={fetchTeamData}
            disabled={loading}
            sx={{
              borderColor: '#667eea',
              color: '#667eea',
            }}
          >
            {loading ? 'Chargement...' : 'Actualiser'}
          </Button>
          <Button
            variant="contained"
            disabled={loading}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            Rebalance Workload
          </Button>
        </Box>
      </Box>

      {loading && teamMembers.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>

      {/* Team Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                Team Size
              </Typography>
              <Typography variant="h3" fontWeight={700}>
                {teamMembers.length}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                members
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                Active Tasks
              </Typography>
              <Typography variant="h3" fontWeight={700}>
                {totalActive}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                in progress
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                Completed This Week
              </Typography>
              <Typography variant="h3" fontWeight={700}>
                {totalCompleted}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                tasks done
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                Avg Burnout Risk
              </Typography>
              <Typography variant="h3" fontWeight={700}>
                {(avgBurnout * 100).toFixed(0)}%
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                team health
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Team Members Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {teamMembers.map((member) => (
          <Grid item xs={12} md={6} lg={3} key={member.id}>
            <Card
              sx={{
                transition: 'all 0.3s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                },
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Avatar
                    sx={{
                      width: 56,
                      height: 56,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      fontWeight: 700,
                      fontSize: '1.2rem',
                    }}
                  >
                    {member.avatar}
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" fontWeight={700}>
                      {member.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {member.role}
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" color="text.secondary">
                      Burnout Risk
                    </Typography>
                    <Chip
                      label={getRiskLabel(member.burnoutRisk)}
                      size="small"
                      sx={{
                        backgroundColor: getRiskColor(member.burnoutRisk),
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '0.7rem',
                      }}
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={member.burnoutRisk * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#E0E0E0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getRiskColor(member.burnoutRisk),
                        borderRadius: 4,
                      },
                    }}
                  />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Active
                    </Typography>
                    <Typography variant="h6" fontWeight={700}>
                      {member.activeTasks}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Completed
                    </Typography>
                    <Typography variant="h6" fontWeight={700}>
                      {member.completedThisWeek}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Workload
                    </Typography>
                    <Typography variant="h6" fontWeight={700}>
                      {member.workloadScore.toFixed(0)}
                    </Typography>
                  </Box>
                </Box>

                <Button variant="outlined" size="small" fullWidth>
                  View Details
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Detailed Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 3 }}>
            Workload Distribution Analysis
          </Typography>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell><strong>Member</strong></TableCell>
                  <TableCell align="center"><strong>Active Tasks</strong></TableCell>
                  <TableCell align="center"><strong>Workload Score</strong></TableCell>
                  <TableCell align="center"><strong>Burnout Risk</strong></TableCell>
                  <TableCell align="center"><strong>Productivity</strong></TableCell>
                  <TableCell align="center"><strong>Status</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {teamMembers.map((member) => (
                  <TableRow key={member.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar
                          sx={{
                            width: 40,
                            height: 40,
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          }}
                        >
                          {member.avatar}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight={600}>
                            {member.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {member.role}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip label={member.activeTasks} size="small" />
                    </TableCell>
                    <TableCell align="center">
                      <Typography
                        variant="body2"
                        fontWeight={600}
                        sx={{
                          color: member.workloadScore > avgWorkload ? '#F44336' : '#4CAF50',
                        }}
                      >
                        {member.workloadScore.toFixed(1)}
                        {member.workloadScore > avgWorkload ? <UpIcon fontSize="small" /> : <DownIcon fontSize="small" />}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={`${(member.burnoutRisk * 100).toFixed(0)}%`}
                        size="small"
                        sx={{
                          backgroundColor: getRiskColor(member.burnoutRisk),
                          color: 'white',
                          fontWeight: 600,
                        }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
                        <Typography variant="body2" fontWeight={600}>
                          {member.productivity}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      {member.burnoutRisk >= 0.6 ? (
                        <Chip icon={<WarningIcon />} label="At Risk" size="small" color="error" />
                      ) : (
                        <Chip icon={<CheckIcon />} label="Healthy" size="small" color="success" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
      </>
      )}
    </Box>
  );
}
