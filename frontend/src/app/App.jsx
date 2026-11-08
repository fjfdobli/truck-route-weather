import { Alert, Box, Typography } from '@mui/material'
import TripMap from '../features/map/TripMap'
import TripForm from '../features/trip-form/TripForm'
import { formatMiles } from '../shared/format'
import { formatDayTime, formatDuration } from '../shared/time'
import { useTripPlan } from './useTripPlan'

export default function App() {
  const { plan, recommended, selectedId, setSelectedId, loading, error, run } = useTripPlan()
  const hasFieldErrors = Object.keys(error?.fields ?? {}).length > 0

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'minmax(0, 1fr) 420px' }, height: { md: '100%' } }}>
      <Box component="main" sx={{ height: { xs: '55vh', md: '100%' } }}>
        <TripMap plan={plan} selectedId={selectedId} onSelect={setSelectedId} />
      </Box>

      <Box sx={{ p: 3, borderLeft: { md: 1 }, borderColor: 'divider', overflowY: { md: 'auto' } }}>
        <Typography variant="h1" component="h1">
          Route weather check
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 3 }}>
          Truck routes rated by the weather on the way.
        </Typography>

        <TripForm onSubmit={run} loading={loading} serverErrors={error?.fields} />

        {error && !hasFieldErrors && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error.message}
          </Alert>
        )}

        {recommended && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h2" component="p">
              Take {recommended.name}. Arrive {formatDayTime(recommended.arrival)}.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatMiles(recommended.distance_mi)} · {formatDuration(recommended.duration_h)} · {plan.reason}
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  )
}
