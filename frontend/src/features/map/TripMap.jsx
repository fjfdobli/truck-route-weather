import 'leaflet/dist/leaflet.css'
import { useEffect, useMemo } from 'react'
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, Tooltip, ZoomControl, useMap } from 'react-leaflet'
import { riskFill } from '../../shared/risk'
import { formatDuration } from '../../shared/time'
import CheckpointPopup from './CheckpointPopup'
import './map.css'

const US_CENTER = [39.5, -98.35]
const LINE = {
  selected: { color: '#1e40af', weight: 6, opacity: 0.95 },
  other: { color: '#64748b', weight: 4, opacity: 0.55 },
}

export default function TripMap({ plan, selectedId, onSelect, focus, showLabels = true, framePadding, children }) {
  const routes = plan?.routes ?? []
  const ordered = [...routes].sort((a, b) => (a.id === selectedId) - (b.id === selectedId))
  const focused = focus && routes.find((r) => r.id === focus.routeId)?.checkpoints[focus.index]

  return (
    <MapContainer center={US_CENTER} zoom={4} preferCanvas zoomControl={false} className="trip-map">
      <ZoomControl position="topright" />
      <TileLayer
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · Routing <a href="https://project-osrm.org/">OSRM</a> · Search <a href="https://photon.komoot.io/">Photon</a> · Weather <a href="https://open-meteo.com/">Open-Meteo</a>'
        maxZoom={19}
      />

      {plan && <FitToRoutes routes={routes} padding={framePadding} />}

      {ordered.map((route) => (
        <RouteLine
          key={`${route.id}-${route.id === selectedId}`}
          route={route}
          selected={route.id === selectedId}
          onSelect={onSelect}
          showLabel={showLabels || route.id === selectedId}
        />
      ))}

      {ordered.map((route) => (
        <Checkpoints key={`${route.id}-${route.id === selectedId}`} route={route} selected={route.id === selectedId} weightLb={plan.weight_lb} />
      ))}

      {plan && (
        <>
          <Endpoint position={[plan.origin.lat, plan.origin.lon]} label={`Start: ${plan.origin.label}`} />
          <Endpoint position={[plan.destination.lat, plan.destination.lon]} label={`End: ${plan.destination.label}`} end />
        </>
      )}

      {focused && (
        <CircleMarker
          center={[focused.lat, focused.lon]}
          radius={12}
          pathOptions={{ color: '#111827', weight: 2, fill: false }}
          interactive={false}
        />
      )}

      {children}
    </MapContainer>
  )
}

const DEFAULT_PADDING = { topLeft: [40, 40], bottomRight: [40, 40] }

// `padding` must be a stable object. Refits when the map box changes size (the timeline
// opening or closing) until the user pans or zooms; after that their view wins.
function FitToRoutes({ routes, padding = DEFAULT_PADDING }) {
  const map = useMap()
  useEffect(() => {
    const points = routes.flatMap((route) => route.geometry)
    if (!points.length) return

    let fitting = false
    let userMoved = false
    const onUserMove = () => {
      if (!fitting) userMoved = true
    }
    const fit = () => {
      map.invalidateSize()
      if (userMoved) return
      fitting = true
      map.fitBounds(points, { paddingTopLeft: padding.topLeft, paddingBottomRight: padding.bottomRight, animate: false })
      fitting = false
    }

    map.on('dragstart zoomstart', onUserMove)
    const observer = new ResizeObserver(fit)
    observer.observe(map.getContainer())
    fit()

    return () => {
      observer.disconnect()
      map.off('dragstart zoomstart', onUserMove)
    }
  }, [map, routes, padding])
  return null
}

function RouteLine({ route, selected, onSelect, showLabel }) {
  const middle = route.geometry[Math.floor(route.geometry.length / 2)]
  const line = selected ? LINE.selected : LINE.other
  return (
    <>
      <Polyline
        positions={route.geometry}
        interactive={false}
        pathOptions={{ color: '#ffffff', weight: line.weight + 4, opacity: 0.9, lineCap: 'round', lineJoin: 'round' }}
      />
      <Polyline
        positions={route.geometry}
        pathOptions={{ ...line, lineCap: 'round', lineJoin: 'round' }}
        eventHandlers={{ click: () => onSelect(route.id) }}
      />
      {showLabel && (
        <CircleMarker center={middle} radius={0} interactive={false}>
          <Tooltip permanent direction="center" className={`route-label${selected ? ' route-label--selected' : ''}`}>
            {route.name} · {formatDuration(route.duration_h)}
          </Tooltip>
        </CircleMarker>
      )}
    </>
  )
}

function Checkpoints({ route, selected, weightLb }) {
  const markers = useMemo(
    () =>
      route.checkpoints.map((cp, index) => (
        <CircleMarker
          key={index}
          center={[cp.lat, cp.lon]}
          radius={selected ? 6 : 3.5}
          pathOptions={{
            color: '#ffffff',
            weight: selected ? 1.5 : 1,
            fillColor: riskFill(cp.risk?.level),
            fillOpacity: selected ? 1 : 0.8,
          }}
        >
          <Popup>
            <CheckpointPopup checkpoint={cp} weightLb={weightLb} />
          </Popup>
        </CircleMarker>
      )),
    [route, selected, weightLb],
  )
  return markers
}

function Endpoint({ position, label, end = false }) {
  return (
    <CircleMarker
      center={position}
      radius={end ? 8 : 7}
      pathOptions={{ color: '#111827', weight: 3, fillColor: end ? '#111827' : '#ffffff', fillOpacity: 1 }}
    >
      <Tooltip>{label}</Tooltip>
    </CircleMarker>
  )
}
