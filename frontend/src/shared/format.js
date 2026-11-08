const whole = new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 })

const plural = (value, one, many) => `${whole.format(value)} ${Math.round(value) === 1 ? one : many}`

export const formatMiles = (miles) => plural(miles, 'mile', 'miles')

export const formatPounds = (pounds) => plural(pounds, 'pound', 'pounds')

export const formatHours = (hours) => plural(hours, 'hour', 'hours')

export function formatAmount(value) {
  return Number(value).toFixed(value > 0 && value < 0.1 ? 2 : 1)
}
