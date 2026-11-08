import { FORECAST_HOURS, hoursBetween } from '../../shared/time'

const HOUR_MS = 3600 * 1000
const TICK_HOURS = 6

export const percentOf = (hours, total = FORECAST_HOURS) => (Math.min(Math.max(hours, 0), total) / total) * 100

// The schedule spans the 48-hour forecast window, or the whole longest drive when it runs past it.
export function axisHours(routes, start) {
  const longest = Math.max(0, ...routes.map((route) => hoursBetween(start, route.arrival)))
  return Math.max(FORECAST_HOURS, Math.ceil(longest / TICK_HOURS) * TICK_HOURS)
}

// Each checkpoint owns the time halfway to its neighbours, so the bar reads as one
// continuous drive from departure to arrival, coloured by the risk met at that time.
export function timeSegments(route, start, total = FORECAST_HOURS) {
  const hours = route.checkpoints.map((cp) => hoursBetween(start, cp.eta))
  const last = hours.length - 1

  return route.checkpoints
    .map((cp, index) => ({
      index,
      from: index === 0 ? hours[0] : (hours[index - 1] + hours[index]) / 2,
      to: index === last ? hours[last] : (hours[index] + hours[index + 1]) / 2,
      level: cp.risk?.level,
      eta: cp.eta,
      mile: cp.mile,
    }))
    .filter((segment) => segment.to > segment.from && segment.from < total)
}

// Neighbouring stretches with the same level become one block: fewer elements, no seams.
export function riskRuns(segments) {
  const runs = []
  for (const { level, from, to } of segments) {
    const last = runs[runs.length - 1]
    if (last && last.level === level) last.to = to
    else runs.push({ level, from, to })
  }
  return runs
}

export function segmentAt(segments, hour) {
  return segments.find((segment) => hour >= segment.from && hour < segment.to) ?? null
}

export function hourAtOffset(offset, length, total = FORECAST_HOURS, exact = false) {
  const hour = Math.min(Math.max(offset / length, 0), 1) * total
  return exact ? hour : Math.round(hour)
}

const hourLabel = new Intl.DateTimeFormat(undefined, { hour: 'numeric' })
const dayLabel = new Intl.DateTimeFormat(undefined, { weekday: 'short' })

// Clock ticks on whole local hours divisible by 6, labelled "6 AM", or the day name at midnight.
export function clockTicks(start, total = FORECAST_HOURS) {
  const startMs = new Date(start).getTime()
  const endMs = startMs + total * HOUR_MS
  const tick = new Date(startMs)
  tick.setMinutes(0, 0, 0)
  while (tick.getTime() <= startMs || tick.getHours() % TICK_HOURS !== 0) tick.setHours(tick.getHours() + 1)

  const ticks = []
  for (; tick.getTime() < endMs; tick.setHours(tick.getHours() + TICK_HOURS)) {
    const midnight = tick.getHours() === 0
    ticks.push({
      hour: (tick.getTime() - startMs) / HOUR_MS,
      label: midnight ? dayLabel.format(tick) : hourLabel.format(tick),
      midnight,
    })
  }
  return ticks
}
