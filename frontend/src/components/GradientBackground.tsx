import { ReactNode } from 'react';
import { Box, useTheme } from '@mui/material';

interface GradientBackgroundProps {
  children: ReactNode;
}

export default function GradientBackground({ children }: GradientBackgroundProps) {
  const theme = useTheme();

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100vh',
        width: '100%',
        backgroundColor: theme.palette.background.default,
        overflow: 'hidden',
        '&::before, &::after': {
          content: '""',
          position: 'absolute',
          width: 420,
          height: 420,
          borderRadius: '50%',
          filter: 'blur(80px)',
          opacity: 0.3,
        },
        '&::before': {
          top: -120,
          right: -100,
          background: 'linear-gradient(135deg, #7c3aed, #60a5fa)',
        },
        '&::after': {
          bottom: -140,
          left: -60,
          background: 'linear-gradient(135deg, #22d3ee, #34d399)',
        },
      }}
    >
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          px: { xs: 2, md: 4 },
          py: { xs: 2, md: 4 },
        }}
      >
        {children}
      </Box>
    </Box>
  );
}

