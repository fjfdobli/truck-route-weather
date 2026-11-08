const STOPS = [
  [22, 163, 74],
  [234, 179, 8],
  [234, 88, 12],
  [220, 38, 38],
  [127, 29, 29],
]

export function riskRgba(value) {
  const v = Math.min(Math.max(value, 0), 4)
  const i = Math.min(Math.floor(v), 3)
  const t = v - i
  const [r, g, b] = STOPS[i].map((c, k) => Math.round(c + (STOPS[i + 1][k] - c) * t))
  const alpha = Math.round(255 * Math.min(Math.max(v - 0.25, 0) * 0.35, 0.75))
  return [r, g, b, alpha]
}

// One small image per forecast hour, one pixel per grid cell. The map stretches it
export function buildHeatFrames({ cells, values, cell_deg: size }) {
  const lats = cells.map(([lat]) => lat)
  const lons = cells.map(([, lon]) => lon)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  const minLon = Math.min(...lons)
  const cols = Math.round((Math.max(...lons) - minLon) / size) + 1
  const rows = Math.round((maxLat - minLat) / size) + 1
  const pixel = cells.map(([lat, lon]) => Math.round((maxLat - lat) / size) * cols + Math.round((lon - minLon) / size))

  const canvas = document.createElement('canvas')
  canvas.width = cols
  canvas.height = rows
  const ctx = canvas.getContext('2d')

  const frames = values.map((hourValues) => {
    const image = ctx.createImageData(cols, rows)
    hourValues.forEach((value, i) => {
      if (value == null) return
      image.data.set(riskRgba(value), pixel[i] * 4)
    })
    ctx.putImageData(image, 0, 0)
    return canvas.toDataURL()
  })

  const half = size / 2
  return {
    frames,
    bounds: [
      [minLat - half, minLon - half],
      [maxLat + half, Math.max(...lons) + half],
    ],
  }
}
