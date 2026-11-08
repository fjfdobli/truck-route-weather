import { Alert, Box, Typography, useMediaQuery } from '@mui/material'
import { useState } from 'react'
import HeatLayer from '../features/forecast/HeatLayer'
import TruckMarkers from '../features/forecast/TruckMarkers'
import { useForecast } from '../features/forecast/useForecast'
import MapStatus from '../features/map/MapStatus'
import TripMap from '../features/map/TripMap'
import SchedulePanel from '../features/timeline/SchedulePanel'
import TripForm from '../features/trip-form/TripForm'
import TripSummary from '../features/trip-form/TripSummary'
import { useTripPlan } from './useTripPlan'

const MAP_FRAME = { topLeft: [40, 40], bottomRight: [56, 40] }

export default function App() {
  const wide = useMediaQuery((theme) => theme.breakpoints.up('md'))
  const { plan, trip, recommended, selectedId, setSelectedId, loading, error, run } = useTripPlan()
  const forecast = useForecast(plan)
  const [focus, setFocus] = useState(null)
  const [editing, setEditing] = useState(true)

  const formOpen = editing || !plan
  const hasFieldErrors = Object.keys(error?.fields ?? {}).length > 0

  const [formKey, setFormKey] = useState(0)

  const submit = async (request) => {
    if (await run(request)) setEditing(false)
  }

  // Back to the current results, dropping unsaved edits: a new key remounts the form from the last trip.
  const cancelChanges = () => {
    setEditing(false)
    setFormKey((key) => key + 1)
  }

  const tripSection = (
    <Box component="header" sx={{ px: 3, pt: 2.5, pb: formOpen ? 3 : 2.5, borderBottom: 1, borderColor: 'divider' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, mb: 2 }}>
        <Box component="img" src="/favicon.svg" alt="" sx={{ width: 28, height: 28 }} />
        <Box>
          <Typography variant="h1" component="h1">
            Route weather check
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Truck routes rated by the weather on the way.
          </Typography>
        </Box>
      </Box>
      <Box sx={{ display: formOpen ? 'block' : 'none' }}>
        <TripForm
          key={formKey}
          initial={trip}
          onSubmit={submit}
          onCancel={plan ? cancelChanges : undefined}
          loading={loading}
          serverErrors={error?.fields}
        />
      </Box>
      {!formOpen && <TripSummary trip={trip} onEdit={() => setEditing(true)} />}
      {error && !hasFieldErrors && (
        <Alert severity="error" sx={{ mt: 2, overflowWrap: 'anywhere' }}>
          {error.message}
        </Alert>
      )}
    </Box>
  )

  const map = (
    <Box component="main" aria-busy={loading} sx={{ position: 'relative', height: wide ? '100%' : '55vh', minHeight: 320 }}>
      <TripMap plan={plan} selectedId={selectedId} onSelect={setSelectedId} focus={focus} showLabels={wide} framePadding={MAP_FRAME}>
        <HeatLayer heat={forecast.heat} hour={forecast.hour} visible={forecast.showHeat} />
        <TruckMarkers tracks={forecast.tracks} time={forecast.time} selectedId={selectedId} />
      </TripMap>
      <MapStatus loading={loading} empty={!plan && !loading} />
    </Box>
  )

  const schedule = plan && (
    <SchedulePanel
      plan={plan}
      recommended={recommended}
      selectedId={selectedId}
      onSelect={setSelectedId}
      onFocus={setFocus}
      forecast={forecast}
    />
  )

  if (!wide) {
    return (
      <Box>
        {tripSection}
        {(plan || loading) && map}
        {schedule}
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: { md: 'minmax(0, 1fr) 420px', lg: 'minmax(0, 1fr) 460px' }, height: '100%' }}>
      {map}
      <Box sx={{ display: 'flex', flexDirection: 'column', borderLeft: 1, borderColor: 'divider', overflowY: 'auto' }}>
        {tripSection}
        {schedule ?? (
          <Typography variant="body2" color="text.secondary" sx={{ p: 3 }}>
            The schedule shows each route hour by hour, coloured by the weather the truck meets.
          </Typography>
        )}
      </Box>
    </Box>
  )
}
