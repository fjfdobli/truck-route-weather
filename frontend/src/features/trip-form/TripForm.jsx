import { Box, Button, TextField, ToggleButton, ToggleButtonGroup, Typography } from '@mui/material'
import PlaceField from './PlaceField'
import { INTERVALS, MAX_WEIGHT_LB } from './tripRules'
import { useTripForm } from './useTripForm'

const FIELD = {
  inline: { origin: '1 1 180px', destination: '1 1 180px', departure: '0 1 220px', weight: '0 1 120px' },
  stacked: { origin: '1 1 100%', destination: '1 1 100%', departure: '3 1 190px', weight: '2 1 110px' },
}

export default function TripForm({ onSubmit, onCancel, initial, loading, serverErrors, inline = false }) {
  const { form, set, bounds, errors, handleSubmit } = useTripForm({ onSubmit, serverErrors, initial })
  const flex = inline ? FIELD.inline : FIELD.stacked

  return (
    <Box
      component="form"
      noValidate
      onSubmit={handleSubmit}
      sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', gap: inline ? 1.5 : 2 }}
    >
      <Box sx={{ flex: flex.origin, minWidth: 0 }}>
        <PlaceField id="origin" label="From" value={form.origin} onChange={set('origin')} error={errors.origin} placeholder="City or address" />
      </Box>

      <Box sx={{ flex: flex.destination, minWidth: 0 }}>
        <PlaceField id="destination" label="To" value={form.destination} onChange={set('destination')} error={errors.destination} placeholder="City or address" />
      </Box>

      <Box sx={{ flex: flex.departure, minWidth: 0 }}>
        <TextField
          id="departure"
          label="Departure"
          type="datetime-local"
          value={form.departure}
          onChange={(e) => set('departure')(e.target.value)}
          error={Boolean(errors.departure)}
          helperText={errors.departure}
          slotProps={{ htmlInput: bounds, inputLabel: { shrink: true } }}
        />
      </Box>

      <Box sx={{ flex: flex.weight, minWidth: 0 }}>
        <TextField
          id="weight"
          label="Load (pounds)"
          type="number"
          value={form.weight}
          onChange={(e) => set('weight')(e.target.value)}
          error={Boolean(errors.weight)}
          helperText={errors.weight}
          slotProps={{ htmlInput: { min: 1, max: MAX_WEIGHT_LB, step: 500, inputMode: 'numeric' } }}
        />
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', columnGap: 1, rowGap: 0.75, flex: inline ? '0 0 auto' : '1 1 100%' }}>
        <Typography variant="body2" component="span" id="interval-label" sx={{ color: 'text.secondary', whiteSpace: 'nowrap' }}>
          Check the weather every
        </Typography>
        <ToggleButtonGroup
          exclusive
          size="small"
          value={form.interval}
          onChange={(_, value) => value && set('interval')(value)}
          aria-labelledby="interval-label"
        >
          {INTERVALS.map((miles) => (
            <ToggleButton key={miles} value={miles}>
              {miles} miles
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Box>

      <Box sx={{ display: 'flex', gap: 1, flex: inline ? '0 0 auto' : '1 1 100%' }}>
        <Button type="submit" variant="contained" disabled={loading} sx={{ minHeight: 40, px: 3, flex: 1 }}>
          {loading ? 'Checking…' : 'Compare routes'}
        </Button>
        {onCancel && (
          <Button variant="text" onClick={onCancel} disabled={loading} sx={{ minHeight: 40 }}>
            Cancel
          </Button>
        )}
      </Box>
    </Box>
  )
}
