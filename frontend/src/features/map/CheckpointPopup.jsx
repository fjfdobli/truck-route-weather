import { formatAmount, formatMiles, formatPounds } from '../../shared/format'
import { riskText } from '../../shared/risk'
import { formatDayTime } from '../../shared/time'

const UNITS = {
  mph: 'miles per hour',
  'in/hr': 'inches per hour',
}

export default function CheckpointPopup({ checkpoint, weightLb }) {
  const { risk, weather } = checkpoint

  return (
    <div className="cp-popup">
      <div className="cp-popup__head">
        {formatMiles(checkpoint.mile)} from the start · {formatDayTime(checkpoint.eta)}
      </div>
      {risk ? (
        <>
          <div className="cp-popup__level" style={{ color: riskText(risk.level) }}>
            {risk.level}
          </div>
          <table>
            <tbody>
              <Row name="Wind" value={weather.wind_mph} unit="mph" level={risk.wind} />
              <Row name="Rain" value={weather.rain_in} unit="in/hr" level={risk.rain} />
              <Row name="Snow" value={weather.snow_in} unit="in/hr" level={risk.snow} />
            </tbody>
          </table>
          {risk.load_raised && <div className="cp-popup__note">Wind level raised because the load is {formatPounds(weightLb)}.</div>}
        </>
      ) : (
        <div className="cp-popup__note">No forecast this far ahead.</div>
      )}
    </div>
  )
}

function Row({ name, value, unit, level }) {
  return (
    <tr>
      <th scope="row">{name}</th>
      <td>
        {formatAmount(value)}{' '}
        <abbr title={UNITS[unit]} className="cp-popup__unit">
          {unit}
        </abbr>
      </td>
      <td style={{ color: riskText(level) }}>{level}</td>
    </tr>
  )
}
