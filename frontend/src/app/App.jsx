import { Alert, Box, Typography } from '@mui/material'
import TripForm from '../features/trip-form/TripForm'
import { formatMiles } from '../shared/format'
import { formatDayTime, formatDuration } from '../shared/time'
import { useTripPlan } from './useTripPlan'

export default function App() {
  const { plan, recommended, loading, error, run } = useTripPlan()
  const hasFieldErrors = Object.keys(error?.fields ?? {}).length > 0

  return (
    <Box sx={{ maxWidth: 460, p: 3 }}>
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
  )
}
