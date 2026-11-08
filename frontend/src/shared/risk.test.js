import { describe, expect, it } from 'vitest'
import { seriousStretches } from './risk'

describe('seriousStretches', () => {
  it('lists only levels with miles, worst first', () => {
    expect(seriousStretches({ no_travel_mi: 0, severe_mi: 12, high_mi: 30 })).toEqual([
      { level: 'Severe', miles: 12 },
      { level: 'High', miles: 30 },
    ])
  })

  it('is empty on a calm route', () => {
    expect(seriousStretches({ no_travel_mi: 0, severe_mi: 0, high_mi: 0 })).toEqual([])
  })
})
