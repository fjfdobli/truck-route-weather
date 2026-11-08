import { Box, ButtonBase, Typography } from '@mui/material'
import { useMemo, useRef, useState } from 'react'
import { formatMiles } from '../../shared/format'
import { riskFill, riskText, seriousStretches } from '../../shared/risk'
import { FORECAST_HOURS, formatClock, formatDayTime, formatDuration } from '../../shared/time'
import { axisHours, clockTicks, hourAtOffset, percentOf, riskRuns, segmentAt, timeSegments } from './timelineScale'

const AXIS = 76
const KEY_STEPS = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1, PageDown: 6, PageUp: -6 }
const pillTime = new Intl.DateTimeFormat(undefined, { weekday: 'short', hour: 'numeric' })

export default function ScheduleTimeline({ plan, selectedId, onSelect, onFocus, hour, onHour, time }) {
  const start = plan.heatmap.start
  const total = useMemo(() => axisHours(plan.routes, start), [plan, start])
  const ticks = useMemo(() => clockTicks(start, total), [start, total])
  const lanes = useMemo(
    () =>
      [...plan.routes]
        .sort((a, b) => a.rank - b.rank)
        .map((route) => {
          const segments = timeSegments(route, start, total)
          return { route, segments, runs: riskRuns(segments), end: segments.at(-1)?.to ?? 0 }
        }),
    [plan, start, total],
  )

  const body = useRef(null)
  const [dragging, setDragging] = useState(false)
  const hovered = useRef(null)
  const columns = `${AXIS}px repeat(${lanes.length}, minmax(0, 1fr))`
  const at = (hours) => `${percentOf(hours, total)}%`

  const hourAt = (event, exact) => {
    const rect = body.current.getBoundingClientRect()
    return hourAtOffset(event.clientY - rect.top, rect.height, total, exact)
  }
  // The forecast layer and trucks only cover 48 hours, so the playhead stops there.
  const scrubTo = (event) => onHour(Math.min(hourAt(event), FORECAST_HOURS))

  const hover = (event) => {
    const lane = lanes.find(({ route }) => String(route.id) === event.target.closest('[data-lane]')?.dataset.lane)
    const segment = lane && segmentAt(lane.segments, hourAt(event, true))
    const key = segment ? `${lane.route.id}:${segment.index}` : null
    if (key === hovered.current) return
    hovered.current = key
    onFocus(segment ? { routeId: lane.route.id, index: segment.index } : null)
  }

  const handleKey = (event) => {
    const step = KEY_STEPS[event.key]
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? FORECAST_HOURS : step !== undefined ? hour + step : null
    if (next === null) return
    event.preventDefault()
    onHour(Math.min(Math.max(next, 0), FORECAST_HOURS))
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ display: 'grid', gridTemplateColumns: columns, columnGap: 1, pb: 1 }}>
        <span />
        {lanes.map(({ route }) => (
          <LaneHeader
            key={route.id}
            route={route}
            recommended={route.id === plan.recommended_id}
            selected={route.id === selectedId}
            onSelect={() => onSelect(route.id)}
          />
        ))}
      </Box>

      <Box
        ref={body}
        onPointerDown={(event) => {
          const lane = event.target.closest('[data-lane]')?.dataset.lane
          if (lane !== undefined) onSelect(Number(lane))
          setDragging(true)
          event.currentTarget.setPointerCapture(event.pointerId)
          scrubTo(event)
        }}
        onPointerMove={(event) => (dragging ? scrubTo(event) : hover(event))}
        onPointerUp={() => setDragging(false)}
        onPointerCancel={() => setDragging(false)}
        onPointerLeave={() => {
          hovered.current = null
          onFocus(null)
        }}
        sx={{
          position: 'relative',
          flex: 1,
          minHeight: 320,
          display: 'grid',
          gridTemplateColumns: columns,
          columnGap: 1,
          touchAction: 'none',
          cursor: dragging ? 'grabbing' : 'row-resize',
          userSelect: 'none',
        }}
      >
        <Box sx={{ position: 'relative' }}>
          {ticks
            .filter((tick) => total <= FORECAST_HOURS || Math.abs(tick.hour - FORECAST_HOURS) > 2)
            .map((tick) => (
            <Typography
              key={tick.hour}
              variant="body2"
              component="span"
              sx={{
                position: 'absolute',
                right: 10,
                top: at(tick.hour),
                transform: 'translateY(-50%)',
                fontSize: 12,
                fontWeight: tick.midnight ? 700 : 400,
                color: tick.midnight ? 'text.primary' : 'text.secondary',
              }}
            >
              {tick.label}
            </Typography>
          ))}
        </Box>

        {lanes.map((lane) => (
          <Lane key={lane.route.id} lane={lane} total={total} start={start} selected={lane.route.id === selectedId} />
        ))}

        <Box aria-hidden="true" sx={{ position: 'absolute', left: AXIS, right: 0, top: 0, bottom: 0, pointerEvents: 'none' }}>
          {ticks.map((tick) => (
            <Box
              key={tick.hour}
              sx={{
                position: 'absolute',
                left: 0,
                right: 0,
                top: at(tick.hour),
                borderTop: 1,
                borderColor: tick.midnight ? 'grey.400' : 'grey.200',
              }}
            />
          ))}
        </Box>

        {total > FORECAST_HOURS && (
          <Box
            sx={{
              position: 'absolute',
              left: AXIS,
              right: 0,
              top: at(FORECAST_HOURS),
              bottom: 0,
              zIndex: 2,
              borderTop: '2px dashed',
              borderColor: 'grey.500',
              bgcolor: 'rgba(255, 255, 255, 0.55)',
              pointerEvents: 'none',
            }}
          />
        )}
        {total > FORECAST_HOURS && (
          <Typography
            variant="body2"
            component="span"
            sx={{
              position: 'absolute',
              left: 0,
              width: AXIS - 10,
              top: at(FORECAST_HOURS),
              transform: 'translateY(-50%)',
              textAlign: 'right',
              fontSize: 12,
              fontWeight: 700,
              bgcolor: 'background.paper',
              zIndex: 3,
            }}
          >
            48 h
          </Typography>
        )}

        <Box
          className="playhead"
          aria-hidden="true"
          sx={{
            position: 'absolute',
            left: AXIS - 6,
            right: 0,
            top: at(hour),
            height: 16,
            transform: 'translateY(-50%)',
            zIndex: 2,
            cursor: dragging ? 'grabbing' : 'grab',
            '&::after': {
              content: '""',
              position: 'absolute',
              left: 0,
              right: 0,
              top: '50%',
              height: dragging ? 3 : 2,
              transform: 'translateY(-50%)',
              bgcolor: dragging ? 'primary.main' : 'text.primary',
              transition: 'background-color 120ms, height 120ms',
            },
            '&:hover::after': { bgcolor: 'primary.main', height: 3 },
          }}
        />
        <Box
          role="slider"
          tabIndex={0}
          aria-label="Forecast time. Drag, or use the arrow keys."
          aria-orientation="vertical"
          aria-valuemin={0}
          aria-valuemax={FORECAST_HOURS}
          aria-valuenow={hour}
          aria-valuetext={`${formatDayTime(time)}, ${hour} hours after departure`}
          onKeyDown={handleKey}
          sx={{
            position: 'absolute',
            left: 0,
            width: AXIS - 4,
            top: at(hour),
            transform: 'translateY(-50%)',
            zIndex: 4,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 0.5,
            py: 0.25,
            borderRadius: 1,
            bgcolor: dragging ? 'primary.main' : 'text.primary',
            color: '#ffffff',
            fontSize: 11,
            fontWeight: 600,
            whiteSpace: 'nowrap',
            cursor: dragging ? 'grabbing' : 'grab',
            transition: 'background-color 120ms',
            '&:hover': { bgcolor: 'primary.main' },
            '&:focus-visible': { outline: '2px solid #1e40af', outlineOffset: 2 },
          }}
        >
          <Box component="svg" viewBox="0 0 8 12" aria-hidden="true" sx={{ width: 7, height: 11, flexShrink: 0, fill: 'currentColor' }}>
            <path d="M4 0 8 4.5H0zM4 12 0 7.5h8z" />
          </Box>
          {pillTime.format(time)}
        </Box>
      </Box>
    </Box>
  )
}

function LaneHeader({ route, recommended, selected, onSelect }) {
  const stretches = seriousStretches(route.summary)
  return (
    <ButtonBase
      onClick={onSelect}
      aria-pressed={selected}
      sx={{
        display: 'block',
        minWidth: 0,
        textAlign: 'left',
        p: 1,
        borderRadius: 1.5,
        borderTop: 3,
        borderColor: selected ? 'primary.main' : 'transparent',
        bgcolor: selected ? '#eef2ff' : 'transparent',
        '&:hover': { bgcolor: selected ? '#eef2ff' : 'grey.50' },
        '&.Mui-focusVisible': { outline: '2px solid #1e40af' },
      }}
    >
      {recommended && (
        <Typography
          variant="body2"
          component="span"
          title="Recommended route"
          sx={{ display: 'inline-block', mb: 0.5, px: 0.75, borderRadius: 1, bgcolor: '#dbeafe', color: 'primary.main', fontWeight: 700, fontSize: 11 }}
        >
          Best
        </Typography>
      )}
      <Typography variant="h2" component="span" sx={{ display: 'block', lineHeight: 1.3, overflowWrap: 'anywhere' }}>
        {route.name}
      </Typography>
      <Typography variant="body2" component="span" sx={{ display: 'block', color: 'text.secondary' }}>
        {formatDuration(route.duration_h)}
        <br />
        {formatMiles(route.distance_mi)}
      </Typography>
      {stretches.map(({ level, miles }) => (
        <Typography key={level} variant="body2" component="span" sx={{ display: 'block', color: riskText(level), fontWeight: 600 }}>
          {formatMiles(miles)} {level}
        </Typography>
      ))}
    </ButtonBase>
  )
}

function Lane({ lane, total, start, selected }) {
  const { route, runs, end } = lane
  const span = Math.min(end, total) || 1
  const endAt = percentOf(end, total)
  const sameDay = new Date(route.arrival).toDateString() === new Date(start).toDateString()

  return (
    <Box data-lane={route.id} sx={{ position: 'relative', borderRadius: 1.5, bgcolor: selected ? '#eef2ff' : 'grey.50' }}>
      <Box
        sx={{
          position: 'absolute',
          left: 10,
          right: 10,
          top: 0,
          height: `${endAt}%`,
          borderRadius: 1.5,
          overflow: 'hidden',
          zIndex: 1,
          pointerEvents: 'none',
        }}
      >
        {runs.map((run) => (
          <Box
            key={run.from}
            sx={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: `${(run.from / span) * 100}%`,
              height: `${((Math.min(run.to, total) - run.from) / span) * 100}%`,
              bgcolor: riskFill(run.level),
            }}
          />
        ))}
      </Box>
      {end <= total && (
        <Typography
          variant="body2"
          component="span"
          sx={{
            position: 'absolute',
            left: '50%',
            top: endAt > 88 ? `calc(${endAt}% - 44px)` : `calc(${endAt}% + 6px)`,
            transform: 'translateX(-50%)',
            zIndex: 3,
            px: 0.75,
            py: 0.25,
            borderRadius: 1,
            border: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
            fontSize: 12,
            lineHeight: 1.25,
            textAlign: 'center',
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
          }}
        >
          <Box component="span" sx={{ color: 'text.secondary' }}>
            Arrive
          </Box>
          <br />
          {sameDay ? formatClock(route.arrival) : formatDayTime(route.arrival)}
        </Typography>
      )}
    </Box>
  )
}
