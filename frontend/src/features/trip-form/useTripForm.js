import { useState } from 'react'
import { MAX_DAYS_AHEAD, addHours, nextFullHour, toLocalInput } from '../../shared/time'
import { fieldErrorsFromServer, fromTripRequest, toTripRequest, validateTrip } from './tripRules'

const emptyForm = () => ({
  origin: '',
  destination: '',
  departure: toLocalInput(nextFullHour()),
  weight: '40000',
  interval: 25,
})

export function useTripForm({ onSubmit, serverErrors, initial }) {
  const [form, setForm] = useState(() => (initial ? fromTripRequest(initial) : emptyForm()))
  const [errors, setErrors] = useState({})
  const [bounds] = useState(() => {
    const now = new Date()
    return { min: toLocalInput(now), max: toLocalInput(addHours(now, MAX_DAYS_AHEAD * 24)) }
  })

  const set = (field) => (value) => {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const found = validateTrip(form)
    setErrors(found)
    if (!Object.keys(found).length) onSubmit(toTripRequest(form))
  }

  return {
    form,
    set,
    bounds,
    handleSubmit,
    errors: { ...errors, ...fieldErrorsFromServer(serverErrors) },
  }
}
