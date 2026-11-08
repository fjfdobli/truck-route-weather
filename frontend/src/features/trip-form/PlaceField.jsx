import { Autocomplete, CircularProgress, TextField } from '@mui/material'
import { useEffect, useState } from 'react'
import { searchPlaces } from '../../api/trips'

const labelOf = (place) => (typeof place === 'string' ? place : place?.label ?? '')

export default function PlaceField({ id, label, value, onChange, error, placeholder }) {
  const [input, setInput] = useState(labelOf(value))
  // Suggestions remember the text they were found for, so older results never show under newer text.
  const [results, setResults] = useState({ query: '', places: [], failed: false })

  const query = input.trim()
  const searchable = query.length >= 3 && !(typeof value === 'object' && value?.label === input)
  const current = searchable && results.query === query
  const loading = searchable && !current

  useEffect(() => {
    if (!searchable) return

    const controller = new AbortController()
    const timer = setTimeout(async () => {
      try {
        setResults({ query, places: (await searchPlaces(query, controller.signal)) ?? [], failed: false })
      } catch (err) {
        if (err.name !== 'AbortError') setResults({ query, places: [], failed: true })
      }
    }, 250)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [query, searchable])

  return (
    <Autocomplete
      id={id}
      freeSolo
      options={current ? results.places : []}
      value={value}
      inputValue={input}
      loading={loading}
      loadingText="Searching…"
      noOptionsText={
        results.failed
          ? 'Place search is not responding. Keep typing to try again.'
          : 'No matching place in the US, Canada or Mexico'
      }
      filterOptions={(all) => all}
      getOptionLabel={labelOf}
      isOptionEqualToValue={(a, b) => a.lat === b.lat && a.lon === b.lon}
      onInputChange={(_, text, reason) => {
        setInput(text)
        if (reason === 'input') onChange(text)
      }}
      onChange={(_, picked) => onChange(picked ?? '')}
      renderOption={(props, place) => (
        <li {...props} key={`${place.lat},${place.lon}`}>
          {place.label}
        </li>
      )}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder={placeholder}
          error={Boolean(error)}
          helperText={error}
          slotProps={{
            ...params.slotProps,
            input: {
              ...params.slotProps.input,
              endAdornment: (
                <>
                  {loading && <CircularProgress size={16} />}
                  {params.slotProps.input.endAdornment}
                </>
              ),
            },
          }}
        />
      )}
    />
  )
}
