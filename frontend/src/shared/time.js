const HOUR = 60 * 60 * 1000
export const MAX_DAYS_AHEAD = 5
export const FORECAST_HOURS = 48

export function nextFullHour(from = new Date()) {
  return new Date(Math.ceil(from.getTime() / HOUR) * HOUR)
}

export function addHours(date, hours) {
  return new Date(date.getTime() + hours * HOUR)
}

export function hoursBetween(from, to) {
  return (new Date(to).getTime() - new Date(from).getTime()) / HOUR
}

export function toLocalInput(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const dayTime = new Intl.DateTimeFormat(undefined, {
  weekday: 'short',
  hour: 'numeric',
  minute: '2-digit',
})

const clock = new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' })

export function formatDayTime(value) {
  return dayTime.format(new Date(value))
}

export function formatClock(value) {
  return clock.format(new Date(value))
}

export function formatDuration(hours) {
  const h = Math.floor(hours)
  const m = Math.round((hours - h) * 60)
  return m === 60 ? `${h + 1} h` : `${h} h ${String(m).padStart(2, '0')} min`
}
