from dataclasses import dataclass
from enum import IntEnum


class Risk(IntEnum):
    LOW = 0
    MODERATE = 1
    HIGH = 2
    SEVERE = 3
    NO_TRAVEL = 4

    @property
    def label(self):
        return self.name.replace('_', ' ').title()


# Each band includes its lower bound, so 0.25 in/hr of rain is High, not Moderate.
WIND_MPH = (
    (Risk.NO_TRAVEL, 55, True),
    (Risk.SEVERE, 45, True),
    (Risk.HIGH, 35, True),
    (Risk.MODERATE, 25, True),
)
RAIN_IN_HR = (
    (Risk.NO_TRAVEL, 1.00, False),
    (Risk.SEVERE, 0.50, True),
    (Risk.HIGH, 0.25, True),
    (Risk.MODERATE, 0.10, True),
)
SNOW_IN_HR = (
    (Risk.NO_TRAVEL, 3.0, False),
    (Risk.SEVERE, 2.0, True),
    (Risk.HIGH, 1.0, True),
    (Risk.MODERATE, 0.5, True),
)

# Wind band -> (weight above which it gets worse, what it becomes).
LOAD_RULES = {
    Risk.SEVERE: (30_000, Risk.NO_TRAVEL),
    Risk.HIGH: (40_000, Risk.SEVERE),
}


@dataclass(frozen=True)
class Assessment:
    level: Risk
    wind: Risk
    rain: Risk
    snow: Risk
    load_raised: bool  # the load rules made the wind worse


def classify(value, bands):
    for level, threshold, inclusive in bands:
        if value > threshold or (inclusive and value == threshold):
            return level
    return Risk.LOW


def wind_risk(wind_mph, weight_lb):
    level = classify(wind_mph, WIND_MPH)
    limit, worse = LOAD_RULES.get(level, (None, level))
    if limit is not None and weight_lb > limit:
        return worse
    return level


def intensity(conditions, weight_lb):
    """Continuous 0-4 version of the risk level, for the heatmap. 40 mph wind -> 2.5 (halfway through High)."""
    if conditions is None:
        return None
    wind = max(_position(conditions.wind_mph, WIND_MPH), wind_risk(conditions.wind_mph, weight_lb))
    rain = _position(conditions.rain_in, RAIN_IN_HR)
    snow = _position(conditions.snow_in, SNOW_IN_HR)
    return round(max(wind, rain, snow), 2)


def _position(value, bands):
    level = classify(value, bands)
    if level == Risk.NO_TRAVEL:
        return float(level)
    edges = [0] + [threshold for _, threshold, _ in reversed(bands)]
    lower, upper = edges[level], edges[level + 1]
    return level + min((value - lower) / (upper - lower), 0.99)


def assess(conditions, weight_lb):
    if conditions is None:
        return None

    base_wind = classify(conditions.wind_mph, WIND_MPH)
    wind = wind_risk(conditions.wind_mph, weight_lb)
    rain = classify(conditions.rain_in, RAIN_IN_HR)
    snow = classify(conditions.snow_in, SNOW_IN_HR)
    return Assessment(max(wind, rain, snow), wind, rain, snow, wind > base_wind)
