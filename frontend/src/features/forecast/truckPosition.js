const EARTH_MILES = 3958.8
const toRad = (deg) => (deg * Math.PI) / 180

function milesBetween([lat1, lon1], [lat2, lon2]) {
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2
  return 2 * EARTH_MILES * Math.asin(Math.sqrt(h))
}

export function prepareTrack(route) {
  const along = [0]
  for (let i = 1; i < route.geometry.length; i++) {
    along.push(along[i - 1] + milesBetween(route.geometry[i - 1], route.geometry[i]))
  }
  return {
    geometry: route.geometry,
    along,
    scale: along[along.length - 1] / route.distance_mi,
    times: route.checkpoints.map((cp) => new Date(cp.eta).getTime()),
    miles: route.checkpoints.map((cp) => cp.mile),
  }
}

// Where the truck is at `time`: the mile comes from the checkpoint ETAs, the position from the road shape.
export function truckAt(track, time) {
  const { times, miles } = track
  if (time <= times[0]) return { position: track.geometry[0], status: 'waiting' }
  if (time >= times[times.length - 1]) return { position: track.geometry[track.geometry.length - 1], status: 'arrived' }

  const i = upperBound(times, time) - 1
  const t = (time - times[i]) / (times[i + 1] - times[i])
  const mile = miles[i] + (miles[i + 1] - miles[i]) * t
  return { position: pointAtMile(track, mile * track.scale), status: 'driving', mile }
}

function pointAtMile({ geometry, along }, mile) {
  const j = Math.max(1, upperBound(along, mile))
  if (j >= along.length) return geometry[geometry.length - 1]
  const span = along[j] - along[j - 1] || 1
  const t = (mile - along[j - 1]) / span
  const [a, b] = [geometry[j - 1], geometry[j]]
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
}

function upperBound(sorted, value) {
  let lo = 0
  let hi = sorted.length
  while (lo < hi) {
    const mid = (lo + hi) >> 1
    if (sorted[mid] <= value) lo = mid + 1
    else hi = mid
  }
  return lo
}
