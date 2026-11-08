export const RISK_LEVELS = ['Low', 'Moderate', 'High', 'Severe', 'No Travel']

const FILL = {
  Low: '#16a34a',
  Moderate: '#eab308',
  High: '#ea580c',
  Severe: '#dc2626',
  'No Travel': '#7f1d1d',
}

const TEXT = {
  Low: '#15803d',
  Moderate: '#a16207',
  High: '#c2410c',
  Severe: '#b91c1c',
  'No Travel': '#7f1d1d',
}

export const UNKNOWN_FILL = '#9ca3af'

export const riskFill = (level) => FILL[level] ?? UNKNOWN_FILL
export const riskText = (level) => TEXT[level] ?? '#4b5563'

const SERIOUS = [
  ['No Travel', 'no_travel_mi'],
  ['Severe', 'severe_mi'],
  ['High', 'high_mi'],
]

export function seriousStretches(summary) {
  return SERIOUS.filter(([, key]) => summary[key] > 0).map(([level, key]) => ({ level, miles: summary[key] }))
}
