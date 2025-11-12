/**
 * Task Card Component - Displays individual task with priority
 */
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  MoreVert as MoreIcon,
  Flag as FlagIcon,
  AccessTime as TimeIcon,
} from '@mui/icons-material';
import { Task, TaskStatus } from '../types/Task';
import { format } from 'date-fns';

interface TaskCardProps {
  task: Task;
  onClick?: () => void;
}

const statusColors: Record<TaskStatus, string> = {
  [TaskStatus.PENDING]: '#FFA726',
  [TaskStatus.IN_PROGRESS]: '#42A5F5',
  [TaskStatus.COMPLETED]: '#66BB6A',
  [TaskStatus.BLOCKED]: '#EF5350',
  [TaskStatus.CANCELLED]: '#BDBDBD',
};

const urgencyColors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336'];

export default function TaskCard({ task, onClick }: TaskCardProps) {
  const priorityScore = task.priority_score || 0;
  const urgencyColor = urgencyColors[task.urgency - 1] || '#9E9E9E';

  const getPriorityLabel = (score: number) => {
    if (score >= 0.8) return 'Critical';
    if (score >= 0.6) return 'High';
    if (score >= 0.4) return 'Medium';
    return 'Low';
  };

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
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
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
          <IconButton size="small">
            <MoreIcon />
          </IconButton>
        </Box>

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
