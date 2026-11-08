import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    primary: { main: '#1e40af' },
    text: { primary: '#111827', secondary: '#4b5563' },
    divider: '#e5e7eb',
    background: { default: '#ffffff' },
    error: { main: '#b91c1c' },
  },
  shape: { borderRadius: 6 },
  typography: {
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    fontSize: 14,
    h1: { fontSize: '1.125rem', fontWeight: 600 },
    h2: { fontSize: '0.875rem', fontWeight: 600 },
    body2: { fontSize: '0.8125rem' },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  components: {
    MuiButton: { defaultProps: { disableElevation: true } },
    MuiTextField: { defaultProps: { size: 'small', fullWidth: true } },
    MuiToggleButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          padding: '6px 16px',
          minHeight: 40,
          color: '#374151',
          '&.Mui-selected, &.Mui-selected:hover': {
            color: '#1e40af',
            backgroundColor: '#eff6ff',
            fontWeight: 600,
          },
        },
      },
    },
  },
})
