/**
 * Burnout Alert Component - Displays burnout risk warnings
 */
import {
  Alert,
  AlertTitle,
  Box,
  LinearProgress,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';
import { BurnoutRiskResponse } from '../types/Analytics';

interface BurnoutAlertProps {
  burnoutData: BurnoutRiskResponse;
}

const riskConfig = {
  low: {
    color: '#4CAF50',
    icon: <CheckIcon />,
    severity: 'success' as const,
    title: 'Low Burnout Risk',
  },
  medium: {
    color: '#FFC107',
    icon: <InfoIcon />,
    severity: 'warning' as const,
    title: 'Medium Burnout Risk',
  },
  high: {
    color: '#FF9800',
    icon: <WarningIcon />,
    severity: 'warning' as const,
    title: 'High Burnout Risk',
  },
  critical: {
    color: '#F44336',
    icon: <ErrorIcon />,
    severity: 'error' as const,
    title: 'Critical Burnout Risk',
  },
};

const trendIcons = {
  improving: <TrendingDown sx={{ color: '#4CAF50' }} />,
  stable: <TrendingFlat sx={{ color: '#FFC107' }} />,
  declining: <TrendingUp sx={{ color: '#F44336' }} />,
};

export default function BurnoutAlert({ burnoutData }: BurnoutAlertProps) {
  const config = riskConfig[burnoutData.risk_level];
  const riskPercentage = burnoutData.current_risk_score * 100;

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Alert
        severity={config.severity}
        icon={config.icon}
        sx={{
          mb: 3,
          '& .MuiAlert-message': { width: '100%' },
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <AlertTitle sx={{ fontWeight: 700, fontSize: '1.2rem' }}>
            {config.title}
          </AlertTitle>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Chip
              icon={trendIcons[burnoutData.trend]}
              label={burnoutData.trend.toUpperCase()}
              size="small"
              sx={{ fontWeight: 600 }}
            />
          </Box>
        </Box>
      </Alert>

      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" fontWeight={600}>
            Current Risk Score
          </Typography>
          <Typography variant="body2" fontWeight={700} sx={{ color: config.color }}>
            {riskPercentage.toFixed(1)}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={riskPercentage}
          sx={{
            height: 12,
            borderRadius: 6,
            backgroundColor: '#E0E0E0',
            '& .MuiLinearProgress-bar': {
              backgroundColor: config.color,
              borderRadius: 6,
            },
          }}
        />
      </Box>

      {Object.keys(burnoutData.factors).length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>
            Contributing Factors
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {Object.entries(burnoutData.factors).map(([factor, value]) => (
              <Chip
                key={factor}
                label={`${factor.replace(/_/g, ' ')}: ${(value * 100).toFixed(0)}%`}
                size="small"
                sx={{
                  backgroundColor: value > 0.7 ? '#FFEBEE' : value > 0.4 ? '#FFF9C4' : '#E8F5E9',
                  color: value > 0.7 ? '#C62828' : value > 0.4 ? '#F57F17' : '#2E7D32',
                  fontWeight: 600,
                  textTransform: 'capitalize',
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      {burnoutData.recommendations.length > 0 && (
        <Box>
          <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>
            Recommendations
          </Typography>
          <List dense>
            {burnoutData.recommendations.map((rec, index) => (
              <ListItem key={index} sx={{ pl: 0 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CheckIcon sx={{ color: config.color, fontSize: 20 }} />
                </ListItemIcon>
                <ListItemText
                  primary={rec}
                  primaryTypographyProps={{
                    variant: 'body2',
                    color: 'text.secondary',
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
}
