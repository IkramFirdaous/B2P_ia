/**
 * Email Extraction Page - Gmail integration with global authentication
 */
import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  TextField,
  CircularProgress,
  Tabs,
  Tab,
  LinearProgress,
} from '@mui/material';
import {
  Email as EmailIcon,
  CloudDownload as DownloadIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useAuth } from '../contexts/AuthContext';
import { emailExtractionService } from '../services/emailExtractionService';
import {
  ExtractedEmail,
  ExtractedTask,
  EmailExtractionStats,
} from '../types/EmailExtraction';

export default function EmailExtraction() {
  const { user } = useAuth();
  const [stats, setStats] = useState<EmailExtractionStats | null>(null);
  const [extractedTasks, setExtractedTasks] = useState<ExtractedTask[]>([]);
  const [extractedEmails, setExtractedEmails] = useState<ExtractedEmail[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [fetchConfig, setFetchConfig] = useState({
    maxEmails: 10,
    unreadOnly: true,
  });
  
  // Get employee ID from authenticated user
  const employeeId = user?.employee_id || '';

  useEffect(() => {
    // User is already authenticated via global OAuth
    // Just load the data
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, tasksData, emailsData] = await Promise.all([
        emailExtractionService.getStats(employeeId),
        emailExtractionService.getExtractedTasks(employeeId),
        emailExtractionService.getExtractedEmails(employeeId),
      ]);
      
      setStats(statsData);
      setExtractedTasks(tasksData);
      setExtractedEmails(emailsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchEmails = async () => {
    setLoading(true);
    try {
      const response = await emailExtractionService.fetchEmails({
        employee_id: employeeId,
        max_emails: fetchConfig.maxEmails,
        unread_only: fetchConfig.unreadOnly,
      });
      
      alert(response.message);
      await loadData();
    } catch (error: any) {
      console.error('Failed to fetch emails:', error);
      alert(error.response?.data?.detail || 'Failed to fetch emails');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (taskId: string) => {
    try {
      await emailExtractionService.approveTask(taskId);
      alert('Task approved and created successfully!');
      await loadData();
    } catch (error) {
      console.error('Failed to approve task:', error);
      alert('Failed to approve task');
    }
  };

  const handleReject = async (taskId: string) => {
    // eslint-disable-next-line no-restricted-globals
    if (!confirm('Are you sure you want to reject this task?')) return;
    
    try {
      await emailExtractionService.rejectTask(taskId);
      await loadData();
    } catch (error) {
      console.error('Failed to reject task:', error);
      alert('Failed to reject task');
    }
  };

  const handleExportCSV = async () => {
    try {
      await emailExtractionService.exportDataset(employeeId, 'csv');
    } catch (error) {
      console.error('Failed to export:', error);
      alert('Failed to export dataset');
    }
  };

  const getUrgencyColor = (level: number) => {
    if (level >= 4) return 'error';
    if (level === 3) return 'warning';
    return 'default';
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
            📧 Email Extraction
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Extract tasks and insights from your Gmail inbox using AI
          </Typography>
        </Box>
        {user && (
          <Chip
            label={`Connected: ${user.email}`}
            color="success"
            icon={<EmailIcon />}
          />
        )}
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Emails Processed
                </Typography>
                <Typography variant="h4">{stats.total_emails_processed}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Tasks Extracted
                </Typography>
                <Typography variant="h4">{stats.total_tasks_extracted}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Pending Review
                </Typography>
                <Typography variant="h4">{stats.pending_approvals}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Fetch Controls */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Max Emails"
                type="number"
                value={fetchConfig.maxEmails}
                onChange={(e) =>
                  setFetchConfig({ ...fetchConfig, maxEmails: parseInt(e.target.value) || 10 })
                }
                InputProps={{ inputProps: { min: 1, max: 50 } }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() =>
                  setFetchConfig({ ...fetchConfig, unreadOnly: !fetchConfig.unreadOnly })
                }
              >
                {fetchConfig.unreadOnly ? 'Unread Only' : 'All Emails'}
              </Button>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
                onClick={handleFetchEmails}
                disabled={loading}
              >
                {loading ? 'Fetching...' : 'Fetch Emails'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <Tabs value={currentTab} onChange={(_, v) => setCurrentTab(v)}>
          <Tab label={`Tasks (${extractedTasks.length})`} />
          <Tab label={`Emails (${extractedEmails.length})`} />
        </Tabs>

        {loading && <LinearProgress />}

        {/* Tasks Tab */}
        {currentTab === 0 && (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Task</TableCell>
                  <TableCell>Urgency</TableCell>
                  <TableCell>Deadline</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {extractedTasks.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography color="text.secondary" sx={{ py: 4 }}>
                        No extracted tasks yet. Fetch emails to get started.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  extractedTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>
                        <Typography variant="subtitle2">{task.task_title}</Typography>
                        {task.task_description && (
                          <Typography variant="caption" color="text.secondary">
                            {task.task_description.substring(0, 100)}...
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`Level ${task.urgency_level || 3}`}
                          color={getUrgencyColor(task.urgency_level || 3)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {task.deadline ? format(new Date(task.deadline), 'MMM dd, yyyy') : 'None'}
                      </TableCell>
                      <TableCell>
                        {!task.approved && (
                          <>
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleApprove(task.id)}
                            >
                              <ApproveIcon />
                            </IconButton>
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleReject(task.id)}
                            >
                              <RejectIcon />
                            </IconButton>
                          </>
                        )}
                        {task.approved && (
                          <Chip label="Approved" color="success" size="small" />
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Emails Tab */}
        {currentTab === 1 && (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Subject</TableCell>
                  <TableCell>From</TableCell>
                  <TableCell>Received</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Tasks</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {extractedEmails.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography color="text.secondary" sx={{ py: 4 }}>
                        No emails processed yet.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  extractedEmails.map((email) => (
                    <TableRow key={email.id}>
                      <TableCell>
                        <Typography variant="subtitle2">{email.subject}</Typography>
                      </TableCell>
                      <TableCell>{email.sender}</TableCell>
                      <TableCell>
                        {format(new Date(email.received_at), 'MMM dd, yyyy HH:mm')}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={email.extraction_status}
                          color={email.extraction_status === 'completed' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {extractedTasks.filter((t) => t.extracted_email_id === email.id).length}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Export Button */}
        <CardContent>
          <Button
            startIcon={<DownloadIcon />}
            onClick={handleExportCSV}
            disabled={extractedTasks.length === 0}
          >
            Export Dataset (CSV)
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
}

