/**
 * Email Extraction Page - Gmail integration and email processing
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
  Alert,
  Tabs,
  Tab,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  Email as EmailIcon,
  CloudDownload as DownloadIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Refresh as RefreshIcon,
  Link as LinkIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { emailExtractionService } from '../services/emailExtractionService';
import {
  ExtractedEmail,
  ExtractedTask,
  EmailExtractionStats,
} from '../types/EmailExtraction';

export default function EmailExtraction() {
  const [stats, setStats] = useState<EmailExtractionStats | null>(null);
  const [extractedTasks, setExtractedTasks] = useState<ExtractedTask[]>([]);
  const [extractedEmails, setExtractedEmails] = useState<ExtractedEmail[]>([]);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [fetchConfig, setFetchConfig] = useState({
    maxEmails: 10,
    unreadOnly: true,
  });
  
  // Mock employee ID - in production, get from auth
  const employeeId = '00000000-0000-0000-0000-000000000001';

  useEffect(() => {
    // Check URL params for OAuth callback
    const params = new URLSearchParams(window.location.search);
    const status = params.get('status');
    
    if (status === 'connected') {
      setConnected(true);
      loadData();
      // Clear URL params
      window.history.replaceState({}, '', '/email-extraction');
    } else {
      // Try to load data anyway - if successful, we're connected
      checkConnection();
    }
  }, []);

  const checkConnection = async () => {
    try {
      // Check if credentials exist in database
      const result = await emailExtractionService.checkConnection(employeeId);
      setConnected(result.connected);
      
      // If connected, load stats too
      if (result.connected) {
        const statsData = await emailExtractionService.getStats(employeeId);
        setStats(statsData);
      }
    } catch (error) {
      console.error('Failed to check connection:', error);
      setConnected(false);
    }
  };

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

  const handleConnectGmail = async () => {
    try {
      const response = await emailExtractionService.initiateGmailConnect(employeeId);
      // Redirect to Google OAuth
      window.location.href = response.auth_url;
    } catch (error) {
      console.error('Failed to connect Gmail:', error);
      alert('Failed to connect Gmail. Please try again.');
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

  const getSentimentColor = (score?: number) => {
    if (!score) return '#9E9E9E';
    if (score > 0.3) return '#4CAF50';
    if (score < -0.3) return '#F44336';
    return '#FFC107';
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Email Extraction 📧
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Connect your Gmail and automatically extract tasks and sentiment from emails
        </Typography>
      </Box>

      {/* Connection Status */}
      {!connected ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography>
              Connect your Gmail account to start extracting tasks from emails
            </Typography>
            <Button
              variant="contained"
              startIcon={<LinkIcon />}
              onClick={handleConnectGmail}
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              }}
            >
              Connect Gmail
            </Button>
          </Box>
        </Alert>
      ) : (
        <Alert severity="success" sx={{ mb: 3 }}>
          Gmail connected successfully! You can now fetch and process emails.
        </Alert>
      )}

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Emails Processed
                </Typography>
                <Typography variant="h4" fontWeight={700}>
                  {stats.total_emails_processed}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Tasks Extracted
                </Typography>
                <Typography variant="h4" fontWeight={700}>
                  {stats.total_tasks_extracted}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Pending Approval
                </Typography>
                <Typography variant="h4" fontWeight={700} color="warning.main">
                  {stats.pending_approvals}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Avg Sentiment
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="h4" fontWeight={700}>
                    {stats.average_sentiment.toFixed(2)}
                  </Typography>
                  <Chip
                    label={stats.average_sentiment > 0 ? 'Positive' : stats.average_sentiment < 0 ? 'Negative' : 'Neutral'}
                    size="small"
                    sx={{
                      bgcolor: getSentimentColor(stats.average_sentiment),
                      color: 'white',
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Fetch Emails Section */}
      {connected && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Fetch Emails
            </Typography>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Max Emails"
                  value={fetchConfig.maxEmails}
                  onChange={(e) =>
                    setFetchConfig({ ...fetchConfig, maxEmails: parseInt(e.target.value) })
                  }
                  InputProps={{ inputProps: { min: 1, max: 50 } }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={loading ? <CircularProgress size={20} /> : <EmailIcon />}
                  onClick={handleFetchEmails}
                  disabled={loading}
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    height: 56,
                  }}
                >
                  {loading ? 'Processing...' : 'Fetch Emails'}
                </Button>
              </Grid>
              <Grid item xs={12} sm={2}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<RefreshIcon />}
                  onClick={loadData}
                  sx={{ height: 56 }}
                >
                  Refresh
                </Button>
              </Grid>
              <Grid item xs={12} sm={2}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<DownloadIcon />}
                  onClick={handleExportCSV}
                  sx={{ height: 56 }}
                >
                  Export CSV
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Card sx={{ mb: 3 }}>
        <Tabs
          value={currentTab}
          onChange={(_, newValue) => setCurrentTab(newValue)}
          sx={{ px: 2 }}
        >
          <Tab label="Extracted Tasks (Dataset)" />
          <Tab label="Processed Emails" />
        </Tabs>
      </Card>

      {/* Content */}
      {currentTab === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Extracted Tasks Dataset
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Task</TableCell>
                    <TableCell>From Email</TableCell>
                    <TableCell>Urgency</TableCell>
                    <TableCell>Sentiment</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {extractedTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {task.task_title}
                        </Typography>
                        {task.task_description && (
                          <Typography variant="caption" color="text.secondary">
                            {task.task_description.substring(0, 100)}...
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {task.extracted_email_id.substring(0, 8)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`Level ${task.urgency_level || 3}`}
                          size="small"
                          color={task.urgency_level && task.urgency_level >= 4 ? 'error' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box
                            sx={{
                              width: 12,
                              height: 12,
                              borderRadius: '50%',
                              bgcolor: getSentimentColor(task.sentiment_score),
                            }}
                          />
                          <Typography variant="caption">
                            {task.sentiment_score?.toFixed(2) || 'N/A'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <LinearProgress
                          variant="determinate"
                          value={(task.confidence_score || 0) * 100}
                          sx={{ width: 60 }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={task.approved ? 'Approved' : 'Pending'}
                          size="small"
                          color={task.approved ? 'success' : 'warning'}
                        />
                      </TableCell>
                      <TableCell>
                        {!task.approved && (
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="Approve & Create Task">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => handleApprove(task.id)}
                              >
                                <ApproveIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Reject">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleReject(task.id)}
                              >
                                <RejectIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {extractedTasks.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="text.secondary">
                  No extracted tasks yet. Fetch emails to get started.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {currentTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Processed Emails
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Subject</TableCell>
                    <TableCell>From</TableCell>
                    <TableCell>Received</TableCell>
                    <TableCell>Tasks Extracted</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {extractedEmails.map((email) => (
                    <TableRow key={email.id}>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {email.subject || '(No Subject)'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">{email.sender}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {format(new Date(email.received_at), 'MMM dd, yyyy')}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={email.extracted_tasks.length}
                          size="small"
                          color="primary"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={email.extraction_status}
                          size="small"
                          color={
                            email.extraction_status === 'completed'
                              ? 'success'
                              : email.extraction_status === 'failed'
                              ? 'error'
                              : 'default'
                          }
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {extractedEmails.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="text.secondary">
                  No emails processed yet.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

