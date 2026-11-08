import { Alert, Box, Checkbox, Divider, FormControlLabel, Slider, Typography } from '@mui/material'
import { useState } from 'react'
import { formatHours } from '../../shared/format'
import { RISK_LEVELS, riskFill } from '../../shared/risk'
import { FORECAST_HOURS, formatDayTime } from '../../shared/time'
import ScheduleTimeline from './ScheduleTimeline'
import { axisHours } from './timelineScale'
import Verdict from './Verdict'

const HINT_KEY = 'truck-routing.playhead-hint-seen'
const HOUR_MARKS = [0, 12, 24, 36, 48].map((value) => ({ value, label: value === 48 ? '48 hours' : String(value) }))

function readHintSeen() {
  try {
    return localStorage.getItem(HINT_KEY) === '1'
  } catch {
    return false
  }
}

export default function SchedulePanel({ plan, recommended, selectedId, onSelect, onFocus, forecast }) {
  const [hintSeen, setHintSeen] = useState(readHintSeen)

  const moveTo = (hour) => {
    forecast.setHour(hour)
    if (hintSeen) return
    setHintSeen(true)
    try {
      localStorage.setItem(HINT_KEY, '1')
    } catch {
      // Private mode or blocked storage: the hint simply shows again next visit.
    }
  }

  return (
    <Box component="section" aria-label="Trip schedule" sx={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      <Box sx={{ px: 3, pt: 2.5 }}>
        <Verdict plan={plan} route={recommended} />
        {plan.warning && (
          <Alert severity="warning" sx={{ mt: 1.5 }}>
            {plan.warning}
          </Alert>
        )}
        {plan.routes.some((route) => route.routing === 'car') && (
          <Alert severity="info" sx={{ mt: 1.5 }}>
            Truck routing was not available for this trip (it covers trips up to about 930 miles), so these routes
            follow car roads and road weight limits are not checked.
          </Alert>
        )}
      </Box>

      <Divider sx={{ my: 2 }} />

      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1, px: 3, pb: 1.5 }}>
        <Typography variant="body2">
          <Box component="span" sx={{ fontWeight: 600 }}>
            Weather at {formatDayTime(forecast.time)}
          </Box>
          <Box component="span" sx={{ color: 'text.secondary' }}>
            {' '}· {forecast.hour === 0 ? 'at departure' : `${formatHours(forecast.hour)} after departure`}
          </Box>
        </Typography>
        <FormControlLabel
          sx={{ mr: 0 }}
          control={<Checkbox size="small" checked={forecast.showHeat} onChange={(e) => forecast.setShowHeat(e.target.checked)} />}
          label={<Typography variant="body2">Weather layer</Typography>}
        />
      </Box>

      <Box sx={{ px: 3.5, pb: 1 }}>
        <Slider
          aria-label="Forecast hour"
          value={forecast.hour}
          min={0}
          max={FORECAST_HOURS}
          step={1}
          marks={HOUR_MARKS}
          valueLabelDisplay="auto"
          valueLabelFormat={(hour) => (hour === 0 ? 'Departure' : `+${formatHours(hour)}`)}
          getAriaValueText={(hour) => `${formatHours(hour)} after departure`}
          onChange={(_, hour) => moveTo(hour)}
          size="small"
        />
      </Box>

      {!hintSeen && (
        <Typography variant="body2" sx={{ mx: 3, mb: 1.5, px: 1.5, py: 0.75, borderRadius: 1, bgcolor: '#eff6ff', color: 'primary.main' }}>
          Drag the slider, or the black line in the schedule, to see the weather at each hour.
        </Typography>
      )}

      <Box sx={{ flex: 1, minHeight: 420, px: 3 }}>
        <ScheduleTimeline
          plan={plan}
          selectedId={selectedId}
          onSelect={onSelect}
          onFocus={onFocus}
          hour={forecast.hour}
          onHour={moveTo}
          time={forecast.time}
        />
      </Box>

      {axisHours(plan.routes, plan.heatmap.start) > FORECAST_HOURS && (
        <Typography variant="body2" color="text.secondary" sx={{ px: 3, pt: 1.5 }}>
          Past the dashed 48 h line the lanes still show each checkpoint&apos;s forecast risk; the slider, trucks and weather layer stop at 48 h.
        </Typography>
      )}

      <Box component="ul" aria-label="Risk colours" sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, listStyle: 'none', m: 0, px: 3, py: 2 }}>
        {RISK_LEVELS.map((level) => (
          <Box component="li" key={level} sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
            <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: riskFill(level) }} />
            <Typography variant="body2">{level}</Typography>
          </Box>
        ))}
      </Box>
    </Box>
  )
}
