/**
 * Balance Alert Component - Displays work-life balance status warnings
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
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';
import { BalanceRiskResponse } from '../types/Analytics';

interface BalanceAlertProps {
  balanceData: BalanceRiskResponse;
}

const balanceLevelConfig = {
  low: {
    color: '#F44336',
    icon: <ErrorIcon />,
    severity: 'error' as const,
    title: 'Low Work-Life Balance',
  },
  medium: {
    color: '#FFC107',
    icon: <InfoIcon />,
    severity: 'warning' as const,
    title: 'Medium Work-Life Balance',
  },
  high: {
    color: '#8BC34A',
    icon: <CheckIcon />,
    severity: 'success' as const,
    title: 'Good Work-Life Balance',
  },
  excellent: {
    color: '#4CAF50',
    icon: <CheckIcon />,
    severity: 'success' as const,
    title: 'Excellent Work-Life Balance',
  },
};

const trendIcons = {
  improving: <TrendingUp sx={{ color: '#4CAF50' }} />,
  stable: <TrendingFlat sx={{ color: '#FFC107' }} />,
  declining: <TrendingDown sx={{ color: '#F44336' }} />,
};

export default function BalanceAlert({ balanceData }: BalanceAlertProps) {
  const config = balanceLevelConfig[balanceData.balance_level as keyof typeof balanceLevelConfig];
  const balancePercentage = balanceData.current_balance_score * 100;

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
              icon={trendIcons[balanceData.trend as keyof typeof trendIcons]}
              label={balanceData.trend.toUpperCase()}
              size="small"
              sx={{ fontWeight: 600 }}
            />
          </Box>
        </Box>
      </Alert>

      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" fontWeight={600}>
            Current Balance Score
          </Typography>
          <Typography variant="body2" fontWeight={700} sx={{ color: config.color }}>
            {balancePercentage.toFixed(1)}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={balancePercentage}
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

      {Object.keys(balanceData.factors).length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>
            Contributing Factors
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {Object.entries(balanceData.factors).map(([factor, value]) => {
              const numValue = value as number;
              return (
                <Chip
                  key={factor}
                  label={`${factor.replace(/_/g, ' ')}: ${(numValue * 100).toFixed(0)}%`}
                  size="small"
                  sx={{
                    backgroundColor: numValue > 0.7 ? '#E8F5E9' : numValue > 0.4 ? '#FFF9C4' : '#FFEBEE',
                    color: numValue > 0.7 ? '#2E7D32' : numValue > 0.4 ? '#F57F17' : '#C62828',
                    fontWeight: 600,
                    textTransform: 'capitalize',
                  }}
                />
              );
            })}
          </Box>
        </Box>
      )}

      {balanceData.recommendations.length > 0 && (
        <Box>
          <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>
            Recommendations
          </Typography>
          <List dense>
            {balanceData.recommendations.map((rec: string, index: number) => (
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
