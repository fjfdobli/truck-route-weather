import { ImageOverlay, Pane } from 'react-leaflet'

export default function HeatLayer({ heat, hour, visible }) {
  if (!heat || !visible) return null
  return (
    <Pane name="heat" style={{ zIndex: 350 }}>
      <ImageOverlay url={heat.frames[hour]} bounds={heat.bounds} className="heat-layer" interactive={false} />
    </Pane>
  )
}
