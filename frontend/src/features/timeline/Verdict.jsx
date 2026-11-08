import { Box, Typography } from '@mui/material'
import { formatMiles } from '../../shared/format'
import { seriousStretches } from '../../shared/risk'
import { formatDayTime } from '../../shared/time'

export default function Verdict({ plan, route }) {
  const stretches = seriousStretches(route.summary)
  const parts = stretches.map(({ level, miles }) => `${formatMiles(miles)} of ${level}`)
  const weather =
    parts.length === 0
      ? 'No High or Severe weather on the way.'
      : `${parts.length > 1 ? `${parts.slice(0, -1).join(', ')} and ${parts.at(-1)}` : parts[0]} weather on the way.`

  return (
    <Box sx={{ minWidth: 0 }}>
      <Typography variant="h2" component="p" sx={{ fontSize: '1rem' }}>
        Take {route.name}. Arrive {formatDayTime(route.arrival)}. {weather}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.25 }}>
        {plan.reason}
      </Typography>
    </Box>
  )
}
