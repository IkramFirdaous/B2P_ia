/**
 * Employees Page - Manage employees and team assignments
 */
import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Edit as EditIcon,
  PersonAdd as AddPersonIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface Employee {
  id: string;
  name: string;
  email: string;
  role: string;
  team_id?: string;
  skills?: string[];
}

interface Team {
  id: string;
  name: string;
  description?: string;
}

export default function Employees() {
  const { token } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  useEffect(() => {
    fetchEmployees();
    fetchTeams();
  }, []);

  const fetchEmployees = async () => {
    if (!token) return;

    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/employees`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEmployees(response.data);
    } catch (err: any) {
      console.error('Failed to fetch employees:', err);
      setError(err.response?.data?.detail || 'Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeams = async () => {
    if (!token) return;

    try {
      const response = await axios.get(`${API_URL}/teams`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTeams(response.data);
    } catch (err: any) {
      console.error('Failed to fetch teams:', err);
    }
  };

  const handleEditEmployee = (employee: Employee) => {
    setSelectedEmployee(employee);
    setOpenDialog(true);
  };

  const handleSaveEmployee = async () => {
    if (!token || !selectedEmployee) return;

    try {
      setLoading(true);
      await axios.put(
        `${API_URL}/employees/${selectedEmployee.id}`,
        {
          name: selectedEmployee.name,
          email: selectedEmployee.email,
          role: selectedEmployee.role,
          team_id: selectedEmployee.team_id || null,
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setSuccessMessage('Employee updated successfully!');
      setOpenDialog(false);
      setSelectedEmployee(null);
      await fetchEmployees();
    } catch (err: any) {
      console.error('Failed to update employee:', err);
      setError(err.response?.data?.detail || 'Failed to update employee');
    } finally {
      setLoading(false);
    }
  };

  const getTeamName = (teamId?: string) => {
    if (!teamId) return 'No Team';
    const team = teams.find(t => t.id === teamId);
    return team?.name || 'Unknown Team';
  };

  return (
    <Box>
      {/* Error/Success Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {successMessage && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Employees Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage employees and their team assignments
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
            onClick={fetchEmployees}
            disabled={loading}
            sx={{
              borderColor: '#667eea',
              color: '#667eea',
            }}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Employees Table */}
      {loading && employees.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Email</strong></TableCell>
                <TableCell><strong>Role</strong></TableCell>
                <TableCell><strong>Team</strong></TableCell>
                <TableCell align="center"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {employees.map((employee) => (
                <TableRow key={employee.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>
                      {employee.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {employee.email}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={employee.role} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getTeamName(employee.team_id)}
                      size="small"
                      color={employee.team_id ? 'primary' : 'default'}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleEditEmployee(employee)}
                    >
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Edit Employee Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6" fontWeight={700}>
            Edit Employee
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedEmployee && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
              <TextField
                label="Name"
                fullWidth
                value={selectedEmployee.name}
                onChange={(e) =>
                  setSelectedEmployee({ ...selectedEmployee, name: e.target.value })
                }
              />
              <TextField
                label="Email"
                fullWidth
                value={selectedEmployee.email}
                onChange={(e) =>
                  setSelectedEmployee({ ...selectedEmployee, email: e.target.value })
                }
              />
              <TextField
                label="Role"
                fullWidth
                value={selectedEmployee.role}
                onChange={(e) =>
                  setSelectedEmployee({ ...selectedEmployee, role: e.target.value })
                }
              />
              <FormControl fullWidth>
                <InputLabel>Team</InputLabel>
                <Select
                  value={selectedEmployee.team_id || ''}
                  label="Team"
                  onChange={(e) =>
                    setSelectedEmployee({
                      ...selectedEmployee,
                      team_id: e.target.value || undefined,
                    })
                  }
                >
                  <MenuItem value="">
                    <em>No Team</em>
                  </MenuItem>
                  {teams.map((team) => (
                    <MenuItem key={team.id} value={team.id}>
                      {team.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSaveEmployee}
            disabled={loading}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
