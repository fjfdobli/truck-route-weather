import { describe, expect, it } from 'vitest'
import { toLocalInput } from '../../shared/time'
import { fieldErrorsFromServer, fromTripRequest, toTripRequest, validateTrip } from './tripRules'

const NOW = new Date(2026, 10, 9, 8, 0)

const form = (overrides = {}) => ({
  origin: 'Dallas, TX',
  destination: { label: 'Houston, Texas, US', lat: 29.76, lon: -95.37 },
  departure: toLocalInput(new Date(2026, 10, 9, 10, 0)),
  weight: '40000',
  interval: 25,
  ...overrides,
})

describe('validateTrip', () => {
  it('accepts a complete trip', () => {
    expect(validateTrip(form(), NOW)).toEqual({})
  })

  it('needs both places', () => {
    const errors = validateTrip(form({ origin: '  ', destination: '' }), NOW)
    expect(Object.keys(errors)).toEqual(['origin', 'destination'])
  })

  it('rejects departures in the past and beyond the forecast', () => {
    expect(validateTrip(form({ departure: toLocalInput(new Date(2026, 10, 9, 6, 0)) }), NOW).departure).toMatch(/past/)
    expect(validateTrip(form({ departure: toLocalInput(new Date(2026, 10, 15, 8, 0)) }), NOW).departure).toMatch(/5 days/)
  })

  it('checks the weight', () => {
    expect(validateTrip(form({ weight: '' }), NOW).weight).toBe('Enter a weight.')
    expect(validateTrip(form({ weight: '0' }), NOW).weight).toBe('Enter a weight.')
    expect(validateTrip(form({ weight: '90000' }), NOW).weight).toMatch(/80,000/)
  })
})

describe('fieldErrorsFromServer', () => {
  it('maps API field names and drops empty ones', () => {
    expect(fieldErrorsFromServer({ weight_lb: 'Too heavy.', departure: undefined })).toEqual({ weight: 'Too heavy.' })
  })
})

describe('fromTripRequest', () => {
  it('turns a submitted trip back into the same form values', () => {
    const original = form()
    expect(fromTripRequest(toTripRequest(original))).toEqual(original)
  })
})

describe('toTripRequest', () => {
  it('converts form text into typed values', () => {
    const request = toTripRequest(form())
    expect(request.weightLb).toBe(40000)
    expect(request.departure).toBeInstanceOf(Date)
    expect(request.intervalMi).toBe(25)
  })
})
