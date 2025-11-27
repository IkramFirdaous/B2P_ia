/**
 * Task Card Component - Displays individual task with priority
 */
import { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  LinearProgress,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  MoreVert as MoreIcon,
  Flag as FlagIcon,
  AccessTime as TimeIcon,
  PlayArrow as StartIcon,
  CheckCircle as CompleteIcon,
  Block as BlockIcon,
  Pending as PendingIcon,
  Mail as EmailIcon,
  EditNote as ManualIcon,
  PersonAdd as AssignedIcon,
  CalendarMonth as CalendarIcon,
  Group as MeetingIcon,
  Psychology as DifficultyIcon,
} from '@mui/icons-material';
import { Task, TaskStatus } from '../types/Task';
import { format } from 'date-fns';

interface TaskCardProps {
  task: Task;
  onClick?: () => void;
  onStatusChange?: (taskId: string, newStatus: TaskStatus) => Promise<void>;
}

const statusColors: Record<TaskStatus, string> = {
  [TaskStatus.PENDING]: '#FFA726',
  [TaskStatus.IN_PROGRESS]: '#42A5F5',
  [TaskStatus.COMPLETED]: '#66BB6A',
  [TaskStatus.BLOCKED]: '#EF5350',
  [TaskStatus.CANCELLED]: '#BDBDBD',
};

const urgencyColors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336'];
const difficultyColors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336'];

// Source badge configuration
const sourceConfig: Record<string, { icon: JSX.Element; color: string; label: string }> = {
  email: { icon: <EmailIcon fontSize="small" />, color: '#4A90E2', label: 'Email' },
  manual: { icon: <ManualIcon fontSize="small" />, color: '#7ED321', label: 'Manual' },
  assigned: { icon: <AssignedIcon fontSize="small" />, color: '#F5A623', label: 'Assigned' },
  meeting: { icon: <MeetingIcon fontSize="small" />, color: '#BD10E0', label: 'Meeting' },
  calendar: { icon: <CalendarIcon fontSize="small" />, color: '#50E3C2', label: 'Calendar' },
};

const statusOptions = [
  { value: TaskStatus.PENDING, label: 'Pending', icon: <PendingIcon fontSize="small" /> },
  { value: TaskStatus.IN_PROGRESS, label: 'In Progress', icon: <StartIcon fontSize="small" /> },
  { value: TaskStatus.COMPLETED, label: 'Completed', icon: <CompleteIcon fontSize="small" /> },
  { value: TaskStatus.BLOCKED, label: 'Blocked', icon: <BlockIcon fontSize="small" /> },
];

export default function TaskCard({ task, onClick, onStatusChange }: TaskCardProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [updating, setUpdating] = useState(false);
  const priorityScore = task.priority_score || 0;
  const urgencyColor = urgencyColors[task.urgency - 1] || '#9E9E9E';

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = (event?: React.MouseEvent) => {
    if (event) event.stopPropagation();
    setAnchorEl(null);
  };

  const handleStatusChange = async (newStatus: TaskStatus, event: React.MouseEvent) => {
    event.stopPropagation();
    handleMenuClose();

    if (onStatusChange && task.id) {
      setUpdating(true);
      try {
        await onStatusChange(task.id, newStatus);
      } catch (error) {
        console.error('Failed to update task status:', error);
      } finally {
        setUpdating(false);
      }
    }
  };

  const getPriorityLabel = (score: number) => {
    if (score >= 0.8) return 'Critical';
    if (score >= 0.6) return 'High';
    if (score >= 0.4) return 'Medium';
    return 'Low';
  };

  const getDifficultyLabel = (difficulty: number) => {
    const labels = ['', 'Easy', 'Medium-Easy', 'Medium', 'Hard', 'Very Hard'];
    return labels[difficulty] || 'Medium';
  };

  const getDifficultyColor = (difficulty: number) => {
    return difficultyColors[difficulty - 1] || '#9E9E9E';
  };

  const taskSource = task.source || 'manual';
  const sourceInfo = sourceConfig[taskSource] || sourceConfig.manual;
  const difficulty = task.difficulty || 3;
  const difficultyColor = getDifficultyColor(difficulty);

  return (
    <Card
      sx={{
        mb: 2,
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
        },
        borderLeft: `4px solid ${urgencyColor}`,
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
            <Chip
              label={task.status.replace('_', ' ')}
              size="small"
              sx={{
                backgroundColor: statusColors[task.status],
                color: 'white',
                fontWeight: 600,
                textTransform: 'uppercase',
                fontSize: '0.7rem',
              }}
            />
            <Tooltip title={`Source: ${sourceInfo.label}`}>
              <Chip
                icon={sourceInfo.icon}
                label={sourceInfo.label}
                size="small"
                sx={{
                  backgroundColor: sourceInfo.color,
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '0.7rem',
                  '& .MuiChip-icon': { color: 'white' },
                }}
              />
            </Tooltip>
            <Tooltip title={`Difficulty: ${getDifficultyLabel(difficulty)}`}>
              <Chip
                icon={<DifficultyIcon />}
                label={`Difficulty ${difficulty}/5`}
                size="small"
                variant="outlined"
                sx={{
                  borderColor: difficultyColor,
                  color: difficultyColor,
                  fontWeight: 600,
                  fontSize: '0.7rem',
                  '& .MuiChip-icon': { color: difficultyColor },
                }}
              />
            </Tooltip>
            <Chip
              icon={<FlagIcon />}
              label={getPriorityLabel(priorityScore)}
              size="small"
              variant="outlined"
              sx={{
                borderColor: urgencyColor,
                color: urgencyColor,
                fontWeight: 600,
              }}
            />
          </Box>
          <IconButton size="small" onClick={handleMenuClick} disabled={updating}>
            <MoreIcon />
          </IconButton>
        </Box>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => handleMenuClose()}
          onClick={(e) => e.stopPropagation()}
        >
          <MenuItem disabled sx={{ fontSize: '0.875rem', fontWeight: 600 }}>
            Change Status
          </MenuItem>
          {statusOptions.map((option) => (
            <MenuItem
              key={option.value}
              onClick={(e) => handleStatusChange(option.value, e)}
              disabled={task.status === option.value}
              sx={{
                backgroundColor:
                  task.status === option.value ? 'action.selected' : 'transparent',
              }}
            >
              <ListItemIcon>{option.icon}</ListItemIcon>
              <ListItemText>{option.label}</ListItemText>
            </MenuItem>
          ))}
        </Menu>

        <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
          {task.title}
        </Typography>

        {task.description && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
            }}
          >
            {task.description}
          </Typography>
        )}

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Priority Score
            </Typography>
            <Typography variant="caption" fontWeight={600}>
              {(priorityScore * 100).toFixed(0)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={priorityScore * 100}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: '#E0E0E0',
              '& .MuiLinearProgress-bar': {
                background: `linear-gradient(90deg, ${urgencyColor} 0%, ${urgencyColor}dd 100%)`,
                borderRadius: 3,
              },
            }}
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          {task.deadline && (
            <Tooltip title="Deadline">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TimeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  {format(new Date(task.deadline), 'MMM dd, yyyy')}
                </Typography>
              </Box>
            </Tooltip>
          )}
          {task.estimated_effort && (
            <Tooltip title="Estimated Effort">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TimeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  {task.estimated_effort}h
                </Typography>
              </Box>
            </Tooltip>
          )}
          <Tooltip title="Urgency Level">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <FlagIcon sx={{ fontSize: 16, color: urgencyColor }} />
              <Typography variant="caption" sx={{ color: urgencyColor, fontWeight: 600 }}>
                Level {task.urgency}
              </Typography>
            </Box>
          </Tooltip>
        </Box>
      </CardContent>
    </Card>
  );
}
