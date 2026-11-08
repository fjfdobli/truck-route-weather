import { request } from './client'

export function searchPlaces(query, signal) {
  return request(`/geocode?q=${encodeURIComponent(query)}`, { signal })
}

export function planTrip({ origin, destination, departure, weightLb, intervalMi }) {
  return request('/plan', {
    body: {
      origin: toPlace(origin),
      destination: toPlace(destination),
      departure: departure.toISOString(),
      weight_lb: weightLb,
      interval_mi: intervalMi,
    },
  })
}

function toPlace(place) {
  return typeof place === 'string' ? { label: place.trim() } : place
}
