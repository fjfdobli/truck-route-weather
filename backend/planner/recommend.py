from dataclasses import dataclass

from risk import Risk


@dataclass
class Summary:
    miles_by_level: dict
    unknown_mi: float
    avg_risk: float
    duration_h: float

    def miles(self, level):
        return self.miles_by_level.get(level, 0.0)

    @property
    def severe_or_worse_mi(self):
        return self.miles(Risk.SEVERE) + self.miles(Risk.NO_TRAVEL)

    def sort_key(self):
        # The brief's order: Severe miles, High miles, average risk, travel time.
        return (
            round(self.severe_or_worse_mi, 1),
            round(self.miles(Risk.HIGH), 1),
            round(self.avg_risk, 2),
            round(self.duration_h, 2),
        )


def summarize(checkpoints, duration_h):
    miles_by_level = {level: 0.0 for level in Risk}
    unknown = weighted = 0.0
    for cp in checkpoints:
        if cp.risk is None:
            unknown += cp.covers_mi
            continue
        miles_by_level[cp.risk.level] += cp.covers_mi
        weighted += cp.risk.level * cp.covers_mi

    known = sum(miles_by_level.values())
    return Summary(miles_by_level, unknown, weighted / known if known else 0.0, duration_h)


def explain(best, runner_up):
    """One line on why `best` beat `runner_up`, using the first rule that told them apart."""
    if runner_up is None:
        return 'Only one route was found.'

    rules = [
        (lambda s: s.severe_or_worse_mi, 'Severe or No Travel'),
        (lambda s: s.miles(Risk.HIGH), 'High'),
    ]
    for miles_of, label in rules:
        mine, theirs = round(miles_of(best), 1), round(miles_of(runner_up), 1)
        if mine != theirs:
            return f'Fewest {label} miles: {mine:g} against {theirs:g} on the next best route.'

    if round(best.avg_risk, 2) != round(runner_up.avg_risk, 2):
        return (
            f'Lower average risk: {best.avg_risk:.2f} against {runner_up.avg_risk:.2f} '
            'on the next best route (0 is Low, 4 is No Travel).'
        )

    saved = runner_up.duration_h - best.duration_h
    return f'Same weather risk as the alternatives, and {saved:.1f} hours faster than the next best route.'


def warning(summaries, best):
    if summaries and all(s.miles(Risk.NO_TRAVEL) > 0 for s in summaries):
        return 'Every route crosses No Travel conditions. Consider a later departure.'
    if best.miles(Risk.NO_TRAVEL) > 0:
        return (
            f'The recommended route still crosses {best.miles(Risk.NO_TRAVEL):.0f} miles of No Travel conditions. '
            'Consider a later departure.'
        )
    if any(s.unknown_mi > 0 for s in summaries):
        return 'Part of the trip is beyond the weather forecast, so those miles are not rated.'
    return None
