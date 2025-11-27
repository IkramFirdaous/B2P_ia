import { createTheme } from '@mui/material/styles';

export const gradients = {
  primary: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
  secondary: 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)',
  accent: 'linear-gradient(135deg, #0ea5e9 0%, #22d3ee 100%)',
  success: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
  warning: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
  surface: 'linear-gradient(145deg, rgba(99,102,241,0.12), rgba(14,165,233,0.1))',
};

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6366f1',
      light: '#a5b4fc',
      dark: '#4c51bf',
    },
    secondary: {
      main: '#ec4899',
      light: '#f472b6',
      dark: '#be185d',
    },
    background: {
      default: '#f4f5fb',
      paper: '#ffffff',
    },
    success: {
      main: '#22c55e',
    },
    warning: {
      main: '#f59e0b',
    },
    error: {
      main: '#ef4444',
    },
    info: {
      main: '#0ea5e9',
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569',
    },
  },
  typography: {
    fontFamily: '"Inter","Segoe UI","Roboto","Helvetica","Arial",sans-serif',
    h1: {
      fontWeight: 800,
      fontSize: '3.2rem',
      letterSpacing: '-0.04em',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2.4rem',
      letterSpacing: '-0.03em',
    },
    h3: {
      fontWeight: 700,
      fontSize: '1.8rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.3rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.1rem',
    },
    subtitle1: {
      fontWeight: 500,
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
      letterSpacing: '0.01em',
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#f4f5fb',
        },
        '::-webkit-scrollbar': {
          width: 8,
          height: 8,
        },
        '::-webkit-scrollbar-thumb': {
          background: 'rgba(99,102,241,0.5)',
          borderRadius: 999,
        },
        '::-webkit-scrollbar-track': {
          background: 'transparent',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          padding: '10px 24px',
          fontWeight: 600,
        },
        containedPrimary: {
          backgroundImage: gradients.primary,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 15px 40px rgba(99,102,241,0.35)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 24,
          border: '1px solid rgba(15,23,42,0.06)',
          boxShadow: '0 25px 50px -12px rgba(15,23,42,0.08)',
          background:
            'linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.95) 100%)',
          backdropFilter: 'blur(12px)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 20,
        },
        elevation1: {
          boxShadow: '0 15px 35px rgba(15,23,42,0.08)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          border: 'none',
          backgroundColor: '#0f172a',
          color: '#e2e8f0',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(255,255,255,0.9)',
          backdropFilter: 'blur(12px)',
          boxShadow: '0 10px 40px rgba(15,23,42,0.08)',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          marginInline: 12,
          color: '#cbd5f5',
          '&.Mui-selected': {
            backgroundColor: 'rgba(255,255,255,0.12)',
            color: '#ffffff',
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          backgroundColor: 'rgba(15,23,42,0.04)',
          '& fieldset': {
            borderColor: 'transparent',
          },
          '&:hover fieldset': {
            borderColor: 'rgba(99,102,241,0.4)',
          },
        },
      },
    },
  },
});

export default theme;

