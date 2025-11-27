/**
 * Task Management Page - View and manage tasks
 */
import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  InputAdornment,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Balance as BalanceIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import TaskCard from '../components/TaskCard';
import { Task, TaskStatus } from '../types/Task';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface Employee {
  id: string;
  name: string;
  email: string;
  role: string;
}

export default function TaskManagement() {
  const { user, token } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentTab, setCurrentTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [rebalancing, setRebalancing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    urgency: 3,
    estimated_effort: 0,
    assigned_to: '',
  });

  // Fetch tasks on component mount
  useEffect(() => {
    fetchTasks();
    fetchEmployees();
  }, []);

  // Auto-refresh every 30 seconds to catch new email tasks
  useEffect(() => {
    const intervalId = setInterval(() => {
      if (token && user && !loading) {
        fetchTasks();
      }
    }, 30000); // 30 seconds

    return () => clearInterval(intervalId);
  }, [token, user, loading]);

  const fetchTasks = async () => {
    if (!token || !user) return;

    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/tasks`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { assigned_to: user.id }
      });
      setTasks(response.data);
    } catch (err: any) {
      console.error('Failed to fetch tasks:', err);
      setError(err.response?.data?.detail || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    if (!token) return;

    try {
      const response = await axios.get(`${API_URL}/employees`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEmployees(response.data);
    } catch (err: any) {
      console.error('Failed to fetch employees:', err);
    }
  };

  const filteredTasks = tasks.filter(task => {
    // Filter by search
    if (searchQuery && !task.title.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }

    // Filter by tab
    if (currentTab === 1 && task.status !== TaskStatus.IN_PROGRESS) return false;
    if (currentTab === 2 && task.status !== TaskStatus.PENDING) return false;
    if (currentTab === 3 && task.status !== TaskStatus.COMPLETED) return false;

    return true;
  });

  const taskStats = {
    all: tasks.length,
    inProgress: tasks.filter(t => t.status === TaskStatus.IN_PROGRESS).length,
    pending: tasks.filter(t => t.status === TaskStatus.PENDING).length,
    completed: tasks.filter(t => t.status === TaskStatus.COMPLETED).length,
  };

  const handleCreateTask = async () => {
    if (!token || !user) return;

    try {
      setLoading(true);
      await axios.post(
        `${API_URL}/tasks`,
        {
          title: newTask.title,
          description: newTask.description,
          urgency: newTask.urgency,
          estimated_effort: newTask.estimated_effort,
          created_by: user.id,
          assigned_to: newTask.assigned_to || user.id,  // Use selected employee or default to current user
          status: 'pending',
          source: 'manual',
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setSuccessMessage('Task created successfully!');
      setOpenDialog(false);
      setNewTask({ title: '', description: '', urgency: 3, estimated_effort: 0, assigned_to: '' });

      // Refresh tasks to show the new one
      await fetchTasks();
    } catch (err: any) {
      console.error('Failed to create task:', err);
      setError(err.response?.data?.detail || 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  const handleRebalanceWorkload = async () => {
    if (!token || !user?.team_id) {
      setError('You must be part of a team to rebalance workload');
      return;
    }

    try {
      setRebalancing(true);
      const response = await axios.post(
        `${API_URL}/tasks/rebalance-workload`,
        null,
        {
          headers: { Authorization: `Bearer ${token}` },
          params: { team_id: user.team_id }
        }
      );

      const { total_reassignments, message } = response.data;
      setSuccessMessage(message || `Workload rebalanced! ${total_reassignments} tasks reassigned.`);

      // Refresh tasks to show updated assignments
      await fetchTasks();
    } catch (err: any) {
      console.error('Failed to rebalance workload:', err);
      setError(err.response?.data?.detail || 'Failed to rebalance workload');
    } finally {
      setRebalancing(false);
    }
  };

  const handleStatusChange = async (taskId: string, newStatus: TaskStatus) => {
    if (!token) return;

    try {
      await axios.put(
        `${API_URL}/tasks/${taskId}`,
        { status: newStatus },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setSuccessMessage(`Task status updated to ${newStatus.replace('_', ' ')}`);

      // Refresh tasks to show updated status
      await fetchTasks();
    } catch (err: any) {
      console.error('Failed to update task status:', err);
      setError(err.response?.data?.detail || 'Failed to update task status');
      throw err;
    }
  };

  return (
    <Box>
      {/* Error/Success Messages */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!successMessage}
        autoHideDuration={4000}
        onClose={() => setSuccessMessage(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccessMessage(null)} severity="success" sx={{ width: '100%' }}>
          {successMessage}
        </Alert>
      </Snackbar>

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Task Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage and track your tasks efficiently
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={rebalancing ? <CircularProgress size={20} /> : <BalanceIcon />}
            onClick={handleRebalanceWorkload}
            disabled={rebalancing || loading}
            sx={{
              borderColor: '#667eea',
              color: '#667eea',
              '&:hover': {
                borderColor: '#764ba2',
                backgroundColor: 'rgba(102, 126, 234, 0.04)',
              },
            }}
          >
            {rebalancing ? 'Rebalancing...' : 'Rebalance Workload'}
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
            disabled={loading}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                opacity: 0.9,
              },
            }}
          >
            New Task
          </Button>
        </Box>
      </Box>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button startIcon={<FilterIcon />} variant="outlined">
                  Filters
                </Button>
                <Button variant="outlined">Sort By</Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card sx={{ mb: 3 }}>
        <Tabs
          value={currentTab}
          onChange={(_, newValue) => setCurrentTab(newValue)}
          sx={{
            px: 2,
            '& .MuiTab-root': { fontWeight: 600 },
          }}
        >
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                All Tasks
                <Chip label={taskStats.all} size="small" />
              </Box>
            }
          />
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                In Progress
                <Chip label={taskStats.inProgress} size="small" color="primary" />
              </Box>
            }
          />
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                Pending
                <Chip label={taskStats.pending} size="small" color="warning" />
              </Box>
            }
          />
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                Completed
                <Chip label={taskStats.completed} size="small" color="success" />
              </Box>
            }
          />
        </Tabs>
      </Card>

      {/* Task List */}
      {loading && tasks.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredTasks.length === 0 ? (
            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ textAlign: 'center', py: 8 }}>
                  <Typography variant="h6" color="text.secondary">
                    No tasks found
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {searchQuery ? 'Try a different search query' : 'Create your first task to get started'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ) : (
            filteredTasks.map(task => (
              <Grid item xs={12} md={6} lg={4} key={task.id}>
                <TaskCard task={task} onStatusChange={handleStatusChange} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Create Task Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6" fontWeight={700}>
            Create New Task
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Task Title"
              fullWidth
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Urgency Level</InputLabel>
              <Select
                value={newTask.urgency}
                label="Urgency Level"
                onChange={(e) => setNewTask({ ...newTask, urgency: e.target.value as number })}
              >
                <MenuItem value={1}>1 - Low</MenuItem>
                <MenuItem value={2}>2 - Medium-Low</MenuItem>
                <MenuItem value={3}>3 - Medium</MenuItem>
                <MenuItem value={4}>4 - High</MenuItem>
                <MenuItem value={5}>5 - Critical</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Estimated Effort (hours)"
              type="number"
              fullWidth
              value={newTask.estimated_effort}
              onChange={(e) => setNewTask({ ...newTask, estimated_effort: parseFloat(e.target.value) })}
            />
            <FormControl fullWidth>
              <InputLabel>Assign To</InputLabel>
              <Select
                value={newTask.assigned_to}
                label="Assign To"
                onChange={(e) => setNewTask({ ...newTask, assigned_to: e.target.value })}
              >
                <MenuItem value={user?.id || ''}>
                  <em>Myself ({user?.name})</em>
                </MenuItem>
                {employees
                  .filter(emp => emp.id !== user?.id)
                  .map((employee) => (
                    <MenuItem key={employee.id} value={employee.id}>
                      {employee.name} - {employee.role}
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateTask}
            disabled={!newTask.title || loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : undefined}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            {loading ? 'Creating...' : 'Create Task'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
