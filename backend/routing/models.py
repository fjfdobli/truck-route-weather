import re
from collections import Counter
from dataclasses import dataclass, field

from common.http import ProviderError


@dataclass
class Route:
    coords: list  # [(lat, lon), ...]
    segment_m: list  # distance between coords[i] and coords[i + 1]
    segment_s: list  # driving time for the same segment
    name: str = ''
    via: list = field(default_factory=list)
    profile: str = 'car'  # 'truck' when the router knew the load
    roads: dict = field(default_factory=dict)  # road number -> metres driven on it

    @property
    def distance_m(self):
        return sum(self.segment_m)

    @property
    def duration_s(self):
        return sum(self.segment_s)


class NoRouteError(ProviderError):
    """The places are fine, but no road connects them. The user can fix this, so it is not a server fault."""


NO_ROUTE = 'No road connects these two places. Pick a start and an end on the same road network.'
TOO_FAR_FROM_ROAD = 'One of the places is too far from a road. Try a nearby town or address.'

ROAD_REF = re.compile(r'^(I|US|[A-Z]{2,4}) ?\d+[A-Z]?\b')


def road_name(distance_by_ref):
    """'I 80 / US 30' from the two road numbers a route spends the most distance on."""
    return ' / '.join(ref for ref, _ in Counter(distance_by_ref).most_common(2))


def name_apart(routes):
    """Routes that share a name get their second road swapped for the longest road only they use."""
    names = []
    for route in routes:
        twins = [other for other in routes if other is not route and other.name == route.name]
        shared = {ref for other in twins for ref in other.roads}
        own = [ref for ref, _ in Counter(route.roads).most_common() if ref not in shared]
        names.append(f'{route.name.split(" / ")[0]} / {own[0]}' if twins and own else route.name)
    for route, name in zip(routes, names, strict=True):
        route.name = name


def road_ref(name):
    match = ROAD_REF.match(name or '')
    return match.group(0) if match else None
