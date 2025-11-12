/**
 * Task Management Page - View and manage tasks
 */
import { useState } from 'react';
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
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import TaskCard from '../components/TaskCard';
import { Task, TaskStatus } from '../types/Task';

// Mock data
const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Implement user authentication system',
    description: 'Create a secure authentication flow with JWT tokens',
    assigned_to: 'user-1',
    created_by: 'manager-1',
    urgency: 5,
    deadline: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    estimated_effort: 8,
    status: TaskStatus.IN_PROGRESS,
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
    description: 'Perform security audit',
    assigned_to: 'user-1',
    created_by: 'manager-1',
    urgency: 4,
    deadline: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    estimated_effort: 4,
    status: TaskStatus.PENDING,
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
    title: 'Design new landing page',
    description: 'Create mockups for the new marketing landing page',
    assigned_to: 'user-1',
    created_by: 'manager-1',
    urgency: 3,
    estimated_effort: 6,
    status: TaskStatus.PENDING,
    priority_score: 0.58,
    dependencies: [],
    source: 'meeting' as any,
    completed_at: undefined,
    actual_effort: undefined,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '4',
    title: 'Fix responsive layout issues',
    description: 'Address mobile layout problems on product pages',
    assigned_to: 'user-1',
    created_by: 'manager-1',
    urgency: 4,
    deadline: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
    estimated_effort: 3,
    status: TaskStatus.COMPLETED,
    priority_score: 0.82,
    dependencies: [],
    source: 'manual' as any,
    completed_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    actual_effort: 2.5,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export default function TaskManagement() {
  const [tasks] = useState<Task[]>(mockTasks);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentTab, setCurrentTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    urgency: 3,
    estimated_effort: 0,
  });

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

  const handleCreateTask = () => {
    // Handle task creation
    console.log('Creating task:', newTask);
    setOpenDialog(false);
    setNewTask({ title: '', description: '', urgency: 3, estimated_effort: 0 });
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Task Management 📋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage and track your tasks efficiently
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
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
              <TaskCard task={task} />
            </Grid>
          ))
        )}
      </Grid>

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
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateTask}
            disabled={!newTask.title}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            Create Task
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
