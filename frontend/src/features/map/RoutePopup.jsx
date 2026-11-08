import { formatMiles } from '../../shared/format'
import { RISK_LEVELS, riskFill } from '../../shared/risk'
import { formatDayTime, formatDuration } from '../../shared/time'

const MILES_KEY = {
  Low: 'low_mi',
  Moderate: 'moderate_mi',
  High: 'high_mi',
  Severe: 'severe_mi',
  'No Travel': 'no_travel_mi',
}

export default function RoutePopup({ route, total }) {
  const { summary } = route
  const levels = RISK_LEVELS.filter((level) => summary[MILES_KEY[level]] > 0)

  return (
    <div className="cp-popup">
      <div className="cp-popup__head">
        {route.rank === 1 ? 'Recommended' : `Choice ${route.rank} of ${total}`} ·{' '}
        {route.routing === 'truck' ? 'truck roads' : 'car roads'}
      </div>
      <div className="cp-popup__level">{route.name}</div>
      <div>
        {formatMiles(route.distance_mi)} · {formatDuration(route.duration_h)} · arrives {formatDayTime(route.arrival)}
      </div>
      <table className="route-popup__miles">
        <tbody>
          {levels.map((level) => (
            <tr key={level}>
              <th>
                <span className="route-popup__swatch" style={{ background: riskFill(level) }} />
                {level}
              </th>
              <td>{formatMiles(summary[MILES_KEY[level]])}</td>
            </tr>
          ))}
          {summary.unknown_mi > 0 && (
            <tr>
              <th>Not rated</th>
              <td>{formatMiles(summary.unknown_mi)}</td>
            </tr>
          )}
        </tbody>
      </table>
      <div className="cp-popup__note">Average risk {summary.avg_risk.toFixed(2)} (0 is Low, 4 is No Travel)</div>
    </div>
  )
}
