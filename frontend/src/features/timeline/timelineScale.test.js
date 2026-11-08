import { describe, expect, it } from 'vitest'
import { axisHours, clockTicks, hourAtOffset, percentOf, riskRuns, segmentAt, timeSegments } from './timelineScale'

const START = '2026-11-09T12:00:00Z'
const at = (hours) => new Date(Date.parse(START) + hours * 3600e3).toISOString()

const route = {
  checkpoints: [
    { mile: 0, eta: at(0), risk: { level: 'Low' } },
    { mile: 25, eta: at(2), risk: { level: 'High' } },
    { mile: 50, eta: at(4), risk: { level: 'Low' } },
  ],
}

describe('axisHours', () => {
  it('is 48 hours for trips that fit the forecast window', () => {
    expect(axisHours([{ arrival: at(4) }, { arrival: at(30) }], START)).toBe(48)
  })

  it('stretches to the longest drive, rounded up to 6 hours', () => {
    expect(axisHours([{ arrival: at(62.2) }, { arrival: at(65.7) }], START)).toBe(66)
  })
})

describe('clockTicks', () => {
  it('lands on whole local hours divisible by 6, with day names at midnight', () => {
    const start = new Date(2026, 10, 8, 4, 30)
    const ticks = clockTicks(start)
    expect(ticks[0].hour).toBeCloseTo(1.5)
    expect(ticks.every((t) => t.hour > 0 && t.hour < 48)).toBe(true)
    expect(ticks.filter((t) => t.midnight)).toHaveLength(2)
    expect(ticks).toHaveLength(8)
  })

  it('covers a longer axis when asked', () => {
    expect(clockTicks(new Date(2026, 10, 8, 4, 30), 72)).toHaveLength(12)
  })
})

describe('timeSegments', () => {
  it('splits the drive halfway between checkpoints', () => {
    const segments = timeSegments(route, START)
    expect(segments.map(({ from, to }) => [from, to])).toEqual([
      [0, 1],
      [1, 3],
      [3, 4],
    ])
    expect(segments[1].level).toBe('High')
  })

  it('drops anything past the axis', () => {
    const late = { checkpoints: [{ eta: at(50) }, { eta: at(60) }] }
    expect(timeSegments(late, START)).toEqual([])
    expect(timeSegments(late, START, 66)).toHaveLength(2)
  })
})

describe('riskRuns and segmentAt', () => {
  const segments = [
    { index: 0, level: 'Low', from: 0, to: 1 },
    { index: 1, level: 'Low', from: 1, to: 2 },
    { index: 2, level: 'High', from: 2, to: 3 },
    { index: 3, level: 'Low', from: 3, to: 4 },
  ]

  it('merges neighbours with the same level', () => {
    expect(riskRuns(segments)).toEqual([
      { level: 'Low', from: 0, to: 2 },
      { level: 'High', from: 2, to: 3 },
      { level: 'Low', from: 3, to: 4 },
    ])
  })

  it('finds the checkpoint driven at a given hour', () => {
    expect(segmentAt(segments, 2.5).index).toBe(2)
    expect(segmentAt(segments, 9)).toBeNull()
  })
})

describe('percentOf and hourAtOffset', () => {
  it('maps hours onto the axis and back', () => {
    expect(percentOf(12)).toBe(25)
    expect(percentOf(-3)).toBe(0)
    expect(percentOf(99)).toBe(100)
    expect(percentOf(33, 66)).toBe(50)
    expect(hourAtOffset(250, 1000)).toBe(12)
    expect(hourAtOffset(500, 1000, 66)).toBe(33)
    expect(hourAtOffset(-5, 1000)).toBe(0)
  })
})
