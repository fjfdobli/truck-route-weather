import { describe, expect, it } from 'vitest'
import { prepareTrack, truckAt } from './truckPosition'

const START = Date.UTC(2026, 10, 9, 12)
const HOUR = 3600 * 1000

// About 69 miles due north, driven at 69 mph.
const route = {
  distance_mi: 69,
  geometry: [
    [35, -100],
    [35.5, -100],
    [36, -100],
  ],
  checkpoints: [
    { mile: 0, eta: new Date(START).toISOString() },
    { mile: 69, eta: new Date(START + HOUR).toISOString() },
  ],
}

describe('truckAt', () => {
  const track = prepareTrack(route)

  it('waits at the start before departure', () => {
    expect(truckAt(track, START - HOUR)).toMatchObject({ status: 'waiting', position: [35, -100] })
  })

  it('is halfway along the road halfway through the drive', () => {
    const { status, mile, position } = truckAt(track, START + HOUR / 2)
    expect(status).toBe('driving')
    expect(mile).toBeCloseTo(34.5)
    expect(position[0]).toBeCloseTo(35.5, 2)
  })

  it('stays at the destination after arrival', () => {
    expect(truckAt(track, START + 2 * HOUR)).toMatchObject({ status: 'arrived', position: [36, -100] })
  })
})
