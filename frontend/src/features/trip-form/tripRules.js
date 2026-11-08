import { MAX_DAYS_AHEAD, addHours, toLocalInput } from '../../shared/time'

export const INTERVALS = [10, 25, 50]
export const MAX_WEIGHT_LB = 80000

const placeText = (place) => String(place?.label ?? place ?? '').trim()

export function validateTrip(form, now = new Date()) {
  const errors = {}
  const departure = new Date(form.departure)

  if (!placeText(form.origin)) errors.origin = 'Enter where the trip starts.'
  if (!placeText(form.destination)) errors.destination = 'Enter where the trip ends.'

  if (Number.isNaN(departure.getTime())) errors.departure = 'Pick a date and time.'
  else if (departure < addHours(now, -1)) errors.departure = 'Departure is in the past.'
  else if (departure > addHours(now, MAX_DAYS_AHEAD * 24)) errors.departure = `Forecasts only reach ${MAX_DAYS_AHEAD} days ahead.`

  const weight = Number(form.weight)
  if (!form.weight || !Number.isFinite(weight) || weight <= 0) errors.weight = 'Enter a weight.'
  else if (weight > MAX_WEIGHT_LB) errors.weight = `Use ${MAX_WEIGHT_LB.toLocaleString()} lb or less.`

  return errors
}

export function fieldErrorsFromServer(fields = {}) {
  const mapped = {
    origin: fields.origin,
    destination: fields.destination,
    departure: fields.departure,
    weight: fields.weight_lb,
  }
  return Object.fromEntries(Object.entries(mapped).filter(([, message]) => message))
}

export function toTripRequest(form) {
  return {
    origin: form.origin,
    destination: form.destination,
    departure: new Date(form.departure),
    weightLb: Number(form.weight),
    intervalMi: form.interval,
  }
}

export function fromTripRequest(trip) {
  return {
    origin: trip.origin,
    destination: trip.destination,
    departure: toLocalInput(trip.departure),
    weight: String(trip.weightLb),
    interval: trip.intervalMi,
  }
}
