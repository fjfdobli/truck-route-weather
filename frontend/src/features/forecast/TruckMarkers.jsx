import L from 'leaflet'
import { Marker, Tooltip } from 'react-leaflet'
import './forecast.css'
import { truckAt } from './truckPosition'

const STATUS = {
  waiting: 'Not left yet',
  arrived: 'Arrived',
}

const TRUCK =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9 1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/></svg>'

const ICONS = {
  selected: L.divIcon({ html: TRUCK, className: 'truck-pin truck-pin--selected', iconSize: [30, 30], iconAnchor: [15, 15] }),
  other: L.divIcon({ html: TRUCK, className: 'truck-pin', iconSize: [24, 24], iconAnchor: [12, 12] }),
}

export default function TruckMarkers({ tracks, time, selectedId }) {
  if (!time) return null
  const now = time.getTime()

  return tracks.map(({ id, track }) => {
    const { position, status, mile } = truckAt(track, now)
    const selected = id === selectedId
    return (
      <Marker
        key={id}
        position={position}
        icon={selected ? ICONS.selected : ICONS.other}
        zIndexOffset={selected ? 1000 : 0}
        keyboard={false}
      >
        <Tooltip direction="top" offset={[0, -14]}>
          {STATUS[status] ?? `Truck at mile ${Math.round(mile)}`}
        </Tooltip>
      </Marker>
    )
  })
}
