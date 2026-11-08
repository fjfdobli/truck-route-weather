import { useMemo, useState } from 'react'
import { addHours } from '../../shared/time'
import { buildHeatFrames } from './heatFrames'
import { prepareTrack } from './truckPosition'

export function useForecast(plan) {
  const [state, setState] = useState({ plan: null, hour: 0, showHeat: true })

  // A new plan starts the slider again at departure.
  const hour = state.plan === plan ? state.hour : 0
  const setHour = (value) => setState((s) => ({ ...s, plan, hour: value }))
  const setShowHeat = (value) => setState((s) => ({ ...s, showHeat: value }))

  const heat = useMemo(() => (plan ? buildHeatFrames(plan.heatmap) : null), [plan])
  const tracks = useMemo(() => (plan ? plan.routes.map((route) => ({ id: route.id, track: prepareTrack(route) })) : []), [plan])
  const start = plan ? new Date(plan.heatmap.start) : null

  return {
    hour,
    setHour,
    showHeat: state.showHeat,
    setShowHeat,
    time: start && addHours(start, hour),
    heat,
    tracks,
  }
}
