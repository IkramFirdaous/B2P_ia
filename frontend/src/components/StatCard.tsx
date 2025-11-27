import { ReactNode } from 'react';
import { Card, CardContent, Stack, Typography, Box, Chip } from '@mui/material';

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  trendLabel?: string;
  trendValue?: string;
  icon: ReactNode;
  gradient?: string;
  chipLabel?: string;
}

export default function StatCard({
  title,
  value,
  subtitle,
  trendLabel,
  trendValue,
  icon,
  gradient,
  chipLabel,
}: StatCardProps) {
  return (
    <Card
      sx={{
        background: gradient || 'rgba(255,255,255,0.9)',
        color: gradient ? '#fff' : 'inherit',
        border: gradient ? 'none' : undefined,
      }}
    >
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Stack spacing={1}>
            <Typography variant="body2" sx={{ opacity: gradient ? 0.9 : 0.7 }}>
              {title}
            </Typography>
            <Typography variant="h3" fontWeight={700}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" sx={{ opacity: gradient ? 0.85 : 0.6 }}>
                {subtitle}
              </Typography>
            )}
          </Stack>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: '50%',
              display: 'grid',
              placeItems: 'center',
              backgroundColor: gradient ? 'rgba(255,255,255,0.25)' : 'rgba(99,102,241,0.08)',
            }}
          >
            {icon}
          </Box>
        </Stack>
        <Stack direction="row" spacing={1.5} alignItems="center" mt={2}>
          {trendLabel && (
            <Typography variant="subtitle2" fontWeight={600}>
              {trendLabel}
            </Typography>
          )}
          {trendValue && (
            <Typography variant="body2" sx={{ opacity: gradient ? 0.95 : 0.7 }}>
              {trendValue}
            </Typography>
          )}
          {chipLabel && (
            <Chip
              label={chipLabel}
              size="small"
              sx={{
                backgroundColor: gradient ? 'rgba(255,255,255,0.2)' : 'rgba(99,102,241,0.1)',
                color: gradient ? '#fff' : 'inherit',
                fontWeight: 600,
              }}
            />
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}

