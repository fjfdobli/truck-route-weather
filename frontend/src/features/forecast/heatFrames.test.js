import { describe, expect, it } from 'vitest'
import { riskRgba } from './heatFrames'

describe('riskRgba', () => {
  it('uses the risk palette at whole levels', () => {
    expect(riskRgba(0).slice(0, 3)).toEqual([22, 163, 74])
    expect(riskRgba(3).slice(0, 3)).toEqual([220, 38, 38])
    expect(riskRgba(4).slice(0, 3)).toEqual([127, 29, 29])
  })

  it('gets more opaque as risk rises, and clamps out-of-range values', () => {
    expect(riskRgba(0)[3]).toBeLessThan(riskRgba(2)[3])
    expect(riskRgba(9)).toEqual(riskRgba(4))
    expect(riskRgba(-1)).toEqual(riskRgba(0))
  })
})
