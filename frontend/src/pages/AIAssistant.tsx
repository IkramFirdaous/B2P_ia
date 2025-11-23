/**
 * AI Assistant Page - Multi-Agent System Interface
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Avatar,
  CircularProgress,
  IconButton,
  Divider,
  Alert,
  Stack,
  Fade,
  Tooltip
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  AutoAwesome as SparkleIcon,
  Lightbulb as LightbulbIcon,
  PlayArrow as PlayIcon,
  Psychology as PsychologyIcon
} from '@mui/icons-material';
import { multiAgentService, AgentResponse } from '../services/multiAgentService';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  agentResponse?: AgentResponse;
  timestamp: Date;
}

interface QuickAction {
  label: string;
  query: string;
  icon: React.ReactNode;
  color: string;
  requiresEmployeeId?: boolean;
  requiresTeamId?: boolean;
}

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [employeeId, setEmployeeId] = useState<number>(1); // Demo default
  const [teamId, setTeamId] = useState<number>(1); // Demo default
  const [examples, setExamples] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickActions: QuickAction[] = [
    {
      label: 'Prioritize Tasks',
      query: 'What should I work on next?',
      icon: <SparkleIcon />,
      color: '#667eea',
      requiresEmployeeId: true
    },
    {
      label: 'Check Burnout',
      query: 'Am I at risk of burnout?',
      icon: <PsychologyIcon />,
      color: '#f093fb',
      requiresEmployeeId: true
    },
    {
      label: 'Team Balance',
      query: 'Is my team workload balanced?',
      icon: <LightbulbIcon />,
      color: '#4facfe',
      requiresTeamId: true
    },
    {
      label: 'My Achievements',
      query: 'Show my recent achievements',
      icon: <PlayIcon />,
      color: '#43e97b',
      requiresEmployeeId: true
    }
  ];

  useEffect(() => {
    loadExamples();
    // Welcome message
    setMessages([
      {
        id: '0',
        type: 'agent',
        content: 'Hello! I\'m your AI Assistant powered by a multi-agent system. I can help you with task prioritization, burnout detection, workload balancing, and more. How can I assist you today?',
        timestamp: new Date()
      }
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadExamples = async () => {
    try {
      const data = await multiAgentService.getExamples();
      setExamples(data);
    } catch (error) {
      console.error('Failed to load examples:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await multiAgentService.smartAssist(
        input,
        employeeId,
        teamId
      );

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: response.message,
        agentResponse: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: `Sorry, I encountered an error: ${error.message || 'Unknown error'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action: QuickAction) => {
    setInput(action.query);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user';

    return (
      <Fade in key={message.id}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: isUser ? 'flex-end' : 'flex-start',
            mb: 2
          }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: isUser ? 'row-reverse' : 'row',
              alignItems: 'flex-start',
              maxWidth: '70%'
            }}
          >
            <Avatar
              sx={{
                bgcolor: isUser ? '#667eea' : '#43e97b',
                width: 36,
                height: 36,
                mx: 1
              }}
            >
              {isUser ? <PersonIcon /> : <BotIcon />}
            </Avatar>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                bgcolor: isUser ? '#667eea' : '#f5f5f5',
                color: isUser ? 'white' : 'text.primary',
                borderRadius: 3,
                border: isUser ? 'none' : '1px solid #e0e0e0'
              }}
            >
              <Typography variant="body1">{message.content}</Typography>

              {message.agentResponse && message.agentResponse.success && (
                <Box sx={{ mt: 2 }}>
                  <Chip
                    size="small"
                    label={message.agentResponse.agent_used}
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      color: 'inherit',
                      mb: 1
                    }}
                  />

                  {message.agentResponse.suggestions &&
                    message.agentResponse.suggestions.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography
                          variant="caption"
                          sx={{ display: 'block', mb: 1, opacity: 0.8 }}
                        >
                          Suggestions:
                        </Typography>
                        <Stack spacing={0.5}>
                          {message.agentResponse.suggestions.map(
                            (suggestion, idx) => (
                              <Typography
                                key={idx}
                                variant="body2"
                                sx={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 1
                                }}
                              >
                                <LightbulbIcon sx={{ fontSize: 16 }} />
                                {suggestion}
                              </Typography>
                            )
                          )}
                        </Stack>
                      </Box>
                    )}
                </Box>
              )}
            </Paper>
          </Box>
        </Box>
      </Fade>
    );
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1
          }}
        >
          AI Assistant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Intelligent multi-agent system to help you manage tasks, prevent burnout, and optimize productivity
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card
            elevation={0}
            sx={{
              background: 'linear-gradient(135deg, #667eea22 0%, #764ba222 100%)',
              border: '1px solid #e0e0e0'
            }}
          >
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                {quickActions.map((action, idx) => (
                  <Grid item xs={12} sm={6} md={3} key={idx}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={action.icon}
                      onClick={() => handleQuickAction(action)}
                      sx={{
                        py: 1.5,
                        borderColor: action.color,
                        color: action.color,
                        '&:hover': {
                          borderColor: action.color,
                          bgcolor: `${action.color}11`
                        }
                      }}
                    >
                      {action.label}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Chat Interface */}
        <Grid item xs={12} md={8}>
          <Card
            elevation={0}
            sx={{
              height: '600px',
              display: 'flex',
              flexDirection: 'column',
              border: '1px solid #e0e0e0'
            }}
          >
            {/* Messages */}
            <Box
              sx={{
                flex: 1,
                overflowY: 'auto',
                p: 3,
                bgcolor: '#fafafa'
              }}
            >
              {messages.map(renderMessage)}
              {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Avatar sx={{ bgcolor: '#43e97b', width: 36, height: 36 }}>
                      <BotIcon />
                    </Avatar>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 2,
                        bgcolor: '#f5f5f5',
                        border: '1px solid #e0e0e0',
                        borderRadius: 3
                      }}
                    >
                      <CircularProgress size={20} />
                    </Paper>
                  </Box>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </Box>

            <Divider />

            {/* Input */}
            <Box sx={{ p: 2, bgcolor: 'white' }}>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  size="small"
                  label="Employee ID"
                  type="number"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(parseInt(e.target.value))}
                  sx={{ width: 120 }}
                />
                <TextField
                  size="small"
                  label="Team ID"
                  type="number"
                  value={teamId}
                  onChange={(e) => setTeamId(parseInt(e.target.value))}
                  sx={{ width: 120 }}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  placeholder="Ask me anything... (e.g., 'What should I work on next?')"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                  multiline
                  maxRows={3}
                />
                <Tooltip title="Send">
                  <IconButton
                    color="primary"
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                    sx={{
                      bgcolor: '#667eea',
                      color: 'white',
                      '&:hover': { bgcolor: '#5568d3' },
                      '&:disabled': { bgcolor: '#e0e0e0' }
                    }}
                  >
                    <SendIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          </Card>
        </Grid>

        {/* Info Panel */}
        <Grid item xs={12} md={4}>
          <Stack spacing={2}>
            <Card elevation={0} sx={{ border: '1px solid #e0e0e0' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Available Agents
                </Typography>
                <Stack spacing={1}>
                  {[
                    { name: 'Task Prioritization', color: '#667eea' },
                    { name: 'Burnout Detection', color: '#f093fb' },
                    { name: 'Workload Balancing', color: '#4facfe' },
                    { name: 'Task Extraction', color: '#fad0c4' },
                    { name: 'Recognition', color: '#43e97b' }
                  ].map((agent, idx) => (
                    <Chip
                      key={idx}
                      label={agent.name}
                      sx={{
                        bgcolor: `${agent.color}22`,
                        color: agent.color,
                        borderLeft: `3px solid ${agent.color}`
                      }}
                    />
                  ))}
                </Stack>
              </CardContent>
            </Card>

            <Alert severity="info" icon={<LightbulbIcon />}>
              The system automatically detects which agent to use based on your
              query. You can ask naturally!
            </Alert>

            <Card elevation={0} sx={{ border: '1px solid #e0e0e0' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Example Queries
                </Typography>
                <Stack spacing={1}>
                  {[
                    'What should I work on next?',
                    'Am I at risk of burnout?',
                    'Show me my achievements',
                    'Balance team workload'
                  ].map((query, idx) => (
                    <Button
                      key={idx}
                      size="small"
                      variant="text"
                      onClick={() => setInput(query)}
                      sx={{
                        justifyContent: 'flex-start',
                        textAlign: 'left',
                        color: 'text.secondary',
                        '&:hover': { color: 'primary.main' }
                      }}
                    >
                      "{query}"
                    </Button>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Stack>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AIAssistant;
