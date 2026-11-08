import { Box, Button, ButtonBase, Typography } from '@mui/material'
import { formatMiles, formatPounds } from '../../shared/format'
import { formatDayTime } from '../../shared/time'

const placeName = (place) => (typeof place === 'string' ? place : place.label)

export default function TripSummary({ trip, onEdit }) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
      <ButtonBase
        onClick={onEdit}
        aria-label="Change trip"
        sx={{
          display: 'block',
          minWidth: 0,
          textAlign: 'left',
          mx: -1,
          px: 1,
          py: 0.5,
          borderRadius: 1,
          '&:hover': { bgcolor: 'grey.50' },
          '&.Mui-focusVisible': { outline: '2px solid #1e40af' },
        }}
      >
        <Typography variant="h2" component="span" sx={{ display: 'block' }}>
          {placeName(trip.origin)} to {placeName(trip.destination)}
        </Typography>
        <Typography variant="body2" component="span" color="text.secondary" sx={{ display: 'block', mt: 0.25 }}>
          {formatDayTime(trip.departure)} · {formatPounds(trip.weightLb)} · weather every {formatMiles(trip.intervalMi)}
        </Typography>
      </ButtonBase>
      <Button variant="outlined" onClick={onEdit} sx={{ flexShrink: 0, minHeight: 40, whiteSpace: 'nowrap' }}>
        Change trip
      </Button>
    </Box>
  )
}
