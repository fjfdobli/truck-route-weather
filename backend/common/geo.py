import math
from dataclasses import dataclass

EARTH_RADIUS_M = 6_371_000
METERS_PER_MILE = 1609.344


@dataclass(frozen=True)
class Point:
    lat: float
    lon: float


def haversine_m(a, b):
    lat1, lat2 = math.radians(a.lat), math.radians(b.lat)
    dlat = lat2 - lat1
    dlon = math.radians(b.lon - a.lon)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))


def shift(point, north_m, east_m):
    dlat = math.degrees(north_m / EARTH_RADIUS_M)
    dlon = math.degrees(east_m / (EARTH_RADIUS_M * math.cos(math.radians(point.lat))))
    return Point(point.lat + dlat, point.lon + dlon)


def miles(meters):
    return meters / METERS_PER_MILE


def simplify(coords, tolerance_deg=0.0005):
    """Douglas-Peucker on (lat, lon) pairs, with a stack instead of recursion."""
    if len(coords) < 3:
        return list(coords)

    scale = math.cos(math.radians(coords[0][0]))
    keep = [False] * len(coords)
    keep[0] = keep[-1] = True
    stack = [(0, len(coords) - 1)]
    tol_sq = tolerance_deg**2

    while stack:
        start, end = stack.pop()
        ay, ax = coords[start][0], coords[start][1] * scale
        by, bx = coords[end][0], coords[end][1] * scale
        dy, dx = by - ay, bx - ax
        length_sq = dx * dx + dy * dy

        worst, worst_i = 0.0, 0
        for i in range(start + 1, end):
            py, px = coords[i][0], coords[i][1] * scale
            if length_sq == 0:
                dist_sq = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
                dist_sq = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if dist_sq > worst:
                worst, worst_i = dist_sq, i

        if worst > tol_sq:
            keep[worst_i] = True
            stack.append((start, worst_i))
            stack.append((worst_i, end))

    return [point for point, kept in zip(coords, keep, strict=True) if kept]
