import { Box, LinearProgress, Typography } from '@mui/material'

export default function MapStatus({ loading, empty }) {
  if (loading) {
    return (
      <LinearProgress
        aria-label="Checking routes"
        sx={{ position: 'absolute', top: 0, left: 0, right: 0, zIndex: 1000 }}
      />
    )
  }

  if (!empty) return null

  return (
    <Box
      sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 1000,
        maxWidth: 320,
        px: 2.5,
        py: 2,
        bgcolor: 'background.paper',
        border: 1,
        borderColor: 'divider',
        borderRadius: 2,
        textAlign: 'center',
        pointerEvents: 'none',
      }}
    >
      <Typography variant="h2" component="p">
        No trip yet
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
        Routes, weather checks and the forecast layer appear here.
      </Typography>
    </Box>
  )
}
