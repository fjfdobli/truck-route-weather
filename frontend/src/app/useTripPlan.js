import { useState } from 'react'
import { planTrip } from '../api/trips'

export function useTripPlan() {
  const [plan, setPlan] = useState(null)
  const [trip, setTrip] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const run = async (request) => {
    setLoading(true)
    setError(null)
    try {
      const result = await planTrip(request)
      setPlan(result)
      setTrip(request)
      setSelectedId(result.recommended_id)
      return true
    } catch (err) {
      // Clear the last result so it is never shown under inputs it doesn't belong to.
      setPlan(null)
      setTrip(null)
      setError(err)
      return false
    } finally {
      setLoading(false)
    }
  }

  const recommended = plan?.routes.find((route) => route.id === plan.recommended_id) ?? null

  return { plan, trip, recommended, selectedId, setSelectedId, loading, error, run }
}
