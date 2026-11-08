import { Alert, Box, Typography } from '@mui/material'
import { useState } from 'react'
import HeatLayer from '../features/forecast/HeatLayer'
import TruckMarkers from '../features/forecast/TruckMarkers'
import { useForecast } from '../features/forecast/useForecast'
import TripMap from '../features/map/TripMap'
import SchedulePanel from '../features/timeline/SchedulePanel'
import TripForm from '../features/trip-form/TripForm'
import { useTripPlan } from './useTripPlan'

export default function App() {
  const { plan, recommended, selectedId, setSelectedId, loading, error, run } = useTripPlan()
  const forecast = useForecast(plan)
  const [focus, setFocus] = useState(null)
  const hasFieldErrors = Object.keys(error?.fields ?? {}).length > 0

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'minmax(0, 1fr) 440px' }, height: { md: '100%' } }}>
      <Box component="main" sx={{ height: { xs: '55vh', md: '100%' } }}>
        <TripMap plan={plan} selectedId={selectedId} onSelect={setSelectedId} focus={focus}>
          <HeatLayer heat={forecast.heat} hour={forecast.hour} visible={forecast.showHeat} />
          <TruckMarkers tracks={forecast.tracks} time={forecast.time} selectedId={selectedId} />
        </TripMap>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', borderLeft: { md: 1 }, borderColor: 'divider', overflowY: { md: 'auto' } }}>
        <Box sx={{ px: 3, pt: 2.5, pb: 3, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h1" component="h1">
            Route weather check
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 2 }}>
            Truck routes rated by the weather on the way.
          </Typography>
          <TripForm onSubmit={run} loading={loading} serverErrors={error?.fields} />
          {error && !hasFieldErrors && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error.message}
            </Alert>
          )}
        </Box>
        {plan && (
          <SchedulePanel
            plan={plan}
            recommended={recommended}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onFocus={setFocus}
            forecast={forecast}
          />
        )}
      </Box>
    </Box>
  )
}
