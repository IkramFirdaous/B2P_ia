/**
 * Email Extraction Page - AI-powered task extraction from Gmail
 */
import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Slider,
  Switch,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Pagination,
  Tooltip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Email as EmailIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Assignment as TaskIcon,
  TrendingUp as TrendingIcon,
  Psychology as AIIcon,
} from '@mui/icons-material';
import { emailExtractionService } from '../services/emailExtractionService';
import {
  ExtractedTask,
  ExtractedEmail,
  ExtractionStats,
  ExtractionStatus,
} from '../types/EmailExtraction';

const EmailExtraction = () => {
  // ============================================================================
  // State Management
  // ============================================================================
  const [stats, setStats] = useState<ExtractionStats | null>(null);
  const [tasks, setTasks] = useState<ExtractedTask[]>([]);
  const [emails, setEmails] = useState<ExtractedEmail[]>([]);

  // Fetch controls
  const [maxEmails, setMaxEmails] = useState<number>(20);
  const [unreadOnly, setUnreadOnly] = useState<boolean>(true);
  const [isFetching, setIsFetching] = useState<boolean>(false);

  // Pagination
  const [tasksPage, setTasksPage] = useState<number>(1);
  const [tasksTotalPages, setTasksTotalPages] = useState<number>(1);
  const [emailsPage, setEmailsPage] = useState<number>(1);
  const [emailsTotalPages, setEmailsTotalPages] = useState<number>(1);

  // UI state
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<ExtractedTask | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState<boolean>(false);

  // ============================================================================
  // Data Fetching
  // ============================================================================

  const loadStats = async () => {
    try {
      const statsData = await emailExtractionService.getStats();
      setStats(statsData);
    } catch (err: any) {
      console.error('Failed to load stats:', err);
    }
  };

  const loadTasks = async (page: number = 1) => {
    try {
      const response = await emailExtractionService.getTasks(page, 20, {
        approved: false, // Show only pending tasks by default
      });
      setTasks(response.tasks);
      setTasksTotalPages(response.total_pages);
      setTasksPage(page);
    } catch (err: any) {
      console.error('Failed to load tasks:', err);
    }
  };

  const loadEmails = async (page: number = 1) => {
    try {
      const response = await emailExtractionService.getEmails(page, 10);
      setEmails(response.emails);
      setEmailsTotalPages(response.total_pages);
      setEmailsPage(page);
    } catch (err: any) {
      console.error('Failed to load emails:', err);
    }
  };

  const loadAll = async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([loadStats(), loadTasks(), loadEmails()]);
    } catch (err: any) {
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  // ============================================================================
  // Actions
  // ============================================================================

  const handleFetchEmails = async () => {
    setIsFetching(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await emailExtractionService.fetchAndProcessEmails({
        max_emails: maxEmails,
        unread_only: unreadOnly,
      });

      if (response.success) {
        setSuccess(response.message);
        // Reload data
        await loadAll();
      } else {
        setError('Email processing failed. Please try again.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch emails');
    } finally {
      setIsFetching(false);
    }
  };

  const handleApproveTask = async (taskId: string) => {
    try {
      const response = await emailExtractionService.approveTask(taskId, {
        create_task: true,
      });

      if (response.success) {
        setSuccess(`Task approved: "${response.task.task_title}"`);
        await loadAll();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to approve task');
    }
  };

  const handleRejectTask = async (taskId: string) => {
    try {
      await emailExtractionService.rejectTask(taskId);
      setSuccess('Task rejected');
      await loadAll();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reject task');
    }
  };

  const handleExportDataset = async () => {
    try {
      await emailExtractionService.downloadDatasetAsCSV(true);
      setSuccess('Dataset exported successfully');
    } catch (err: any) {
      setError('Failed to export dataset');
    }
  };

  const handleViewDetails = (task: ExtractedTask) => {
    setSelectedTask(task);
    setDetailsDialogOpen(true);
  };

  // ============================================================================
  // Helper Functions
  // ============================================================================

  const getUrgencyColor = (urgency: number): 'error' | 'warning' | 'info' | 'success' => {
    if (urgency >= 5) return 'error';
    if (urgency >= 4) return 'warning';
    if (urgency >= 3) return 'info';
    return 'success';
  };

  const getStatusColor = (status: ExtractionStatus): 'success' | 'error' | 'warning' | 'default' => {
    switch (status) {
      case ExtractionStatus.COMPLETED:
        return 'success';
      case ExtractionStatus.FAILED:
        return 'error';
      case ExtractionStatus.PROCESSING:
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  // ============================================================================
  // Render
  // ============================================================================

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          <EmailIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Email Task Extraction
        </Typography>
        <Typography variant="body1" color="text.secondary">
          AI-powered task extraction from your Gmail inbox using Gemini
        </Typography>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Stats Dashboard */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <EmailIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Emails Processed</Typography>
              </Box>
              <Typography variant="h3">{stats?.emails.total || 0}</Typography>
              <Typography variant="caption" color="text.secondary">
                {stats?.emails.completed || 0} completed, {stats?.emails.failed || 0} failed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TaskIcon color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6">Tasks Extracted</Typography>
              </Box>
              <Typography variant="h3">{stats?.tasks.total || 0}</Typography>
              <Typography variant="caption" color="text.secondary">
                {stats?.tasks.approved || 0} approved
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AIIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Pending Review</Typography>
              </Box>
              <Typography variant="h3">{stats?.tasks.pending_review || 0}</Typography>
              <Typography variant="caption" color="text.secondary">
                Awaiting your approval
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Success Rate</Typography>
              </Box>
              <Typography variant="h3">
                {stats?.emails.total
                  ? Math.round((stats.emails.completed / stats.emails.total) * 100)
                  : 0}
                %
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Email processing success
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Fetch Controls */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Fetch New Emails
          </Typography>

          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Maximum Emails to Fetch: {maxEmails}
              </Typography>
              <Slider
                value={maxEmails}
                onChange={(_, value) => setMaxEmails(value as number)}
                min={1}
                max={100}
                marks={[
                  { value: 1, label: '1' },
                  { value: 20, label: '20' },
                  { value: 50, label: '50' },
                  { value: 100, label: '100' },
                ]}
                valueLabelDisplay="auto"
                disabled={isFetching}
              />
            </Grid>

            <Grid item xs={12} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={unreadOnly}
                    onChange={(e) => setUnreadOnly(e.target.checked)}
                    disabled={isFetching}
                  />
                }
                label="Unread Only"
              />
            </Grid>

            <Grid item xs={12} md={3}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={isFetching ? <CircularProgress size={20} /> : <RefreshIcon />}
                onClick={handleFetchEmails}
                disabled={isFetching}
              >
                {isFetching ? 'Fetching...' : 'Fetch Emails'}
              </Button>
            </Grid>
          </Grid>

          {isFetching && (
            <Box mt={2}>
              <LinearProgress />
              <Typography variant="caption" color="text.secondary" mt={1}>
                Processing emails with AI... This may take a moment.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Tasks Table */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Extracted Tasks (Pending Review)</Typography>
            <Button
              startIcon={<DownloadIcon />}
              onClick={handleExportDataset}
              size="small"
              variant="outlined"
            >
              Export Dataset
            </Button>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell align="center">Urgency</TableCell>
                  <TableCell align="center">Confidence</TableCell>
                  <TableCell>Deadline</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tasks.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No pending tasks. Fetch emails to extract tasks.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  tasks.map((task) => (
                    <TableRow key={task.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {task.task_title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {task.task_description.substring(0, 60)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">{task.email_subject}</Typography>
                        <br />
                        <Typography variant="caption" color="text.secondary">
                          From: {task.email_sender}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={task.urgency_level}
                          color={getUrgencyColor(task.urgency_level)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="body2">
                          {Math.round(task.confidence_score * 100)}%
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {task.deadline ? (
                          <Typography variant="caption">
                            {formatDate(task.deadline)}
                          </Typography>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            No deadline
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(task)}
                          >
                            <InfoIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Approve & Create Task">
                          <IconButton
                            size="small"
                            color="success"
                            onClick={() => handleApproveTask(task.id)}
                          >
                            <ApproveIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Reject">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleRejectTask(task.id)}
                          >
                            <RejectIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {tasksTotalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={2}>
              <Pagination
                count={tasksTotalPages}
                page={tasksPage}
                onChange={(_, page) => loadTasks(page)}
                color="primary"
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Email History */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Email Processing History
          </Typography>

          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Subject</TableCell>
                  <TableCell>Sender</TableCell>
                  <TableCell>Received</TableCell>
                  <TableCell align="center">Tasks</TableCell>
                  <TableCell align="center">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {emails.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No emails processed yet.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  emails.map((email) => (
                    <TableRow key={email.id} hover>
                      <TableCell>{email.subject}</TableCell>
                      <TableCell>{email.sender}</TableCell>
                      <TableCell>{formatDate(email.received_at)}</TableCell>
                      <TableCell align="center">
                        <Chip label={email.tasks_count} size="small" />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={email.extraction_status}
                          color={getStatusColor(email.extraction_status)}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {emailsTotalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={2}>
              <Pagination
                count={emailsTotalPages}
                page={emailsPage}
                onChange={(_, page) => loadEmails(page)}
                color="primary"
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Task Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Task Details</DialogTitle>
        <DialogContent>
          {selectedTask && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedTask.task_title}
              </Typography>
              <Typography variant="body2" paragraph>
                {selectedTask.task_description}
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Urgency
                  </Typography>
                  <Typography>{selectedTask.urgency_level} / 5</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Confidence
                  </Typography>
                  <Typography>
                    {Math.round(selectedTask.confidence_score * 100)}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Priority Score
                  </Typography>
                  <Typography>
                    {Math.round(selectedTask.priority_score * 100)}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Sentiment
                  </Typography>
                  <Typography>
                    {selectedTask.sentiment_label || 'N/A'} (
                    {selectedTask.sentiment_score?.toFixed(2) || 'N/A'})
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary">
                    From Email
                  </Typography>
                  <Typography variant="body2">
                    {selectedTask.email_subject}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {selectedTask.email_sender}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
          {selectedTask && (
            <>
              <Button
                onClick={() => {
                  handleRejectTask(selectedTask.id);
                  setDetailsDialogOpen(false);
                }}
                color="error"
              >
                Reject
              </Button>
              <Button
                onClick={() => {
                  handleApproveTask(selectedTask.id);
                  setDetailsDialogOpen(false);
                }}
                variant="contained"
                color="success"
              >
                Approve & Create Task
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EmailExtraction;
