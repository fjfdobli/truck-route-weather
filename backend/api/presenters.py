from common.geo import miles, simplify
from risk import Risk


def place_json(place):
    return {'label': place.label, 'lat': place.lat, 'lon': place.lon}


def trip_json(trip, request_data, origin, destination):
    return {
        'origin': place_json(origin),
        'destination': place_json(destination),
        'departure': request_data['departure'],
        'interval_mi': request_data['interval_mi'],
        'weight_lb': request_data['weight_lb'],
        'recommended_id': trip.recommended,
        'reason': trip.reason,
        'warning': trip.warning,
        'routes': [route_json(i, plan, trip.ranking.index(i) + 1) for i, plan in enumerate(trip.routes)],
        'heatmap': heatmap_json(trip.heatmap),
    }


def heatmap_json(heatmap):
    return {
        'start': heatmap.start,
        'cell_deg': heatmap.cell_deg,
        'cells': heatmap.cells,
        'values': heatmap.values,
    }


def route_json(index, plan, rank):
    route, summary = plan.route, plan.summary
    return {
        'id': index,
        'rank': rank,
        'name': route.name or f'Route {index + 1}',
        'routing': route.profile,
        'distance_mi': round(miles(route.distance_m), 1),
        'duration_h': round(summary.duration_h, 2),
        'arrival': plan.arrival,
        'summary': {
            'no_travel_mi': round(summary.miles(Risk.NO_TRAVEL), 1),
            'severe_mi': round(summary.miles(Risk.SEVERE), 1),
            'high_mi': round(summary.miles(Risk.HIGH), 1),
            'moderate_mi': round(summary.miles(Risk.MODERATE), 1),
            'low_mi': round(summary.miles(Risk.LOW), 1),
            'unknown_mi': round(summary.unknown_mi, 1),
            'avg_risk': round(summary.avg_risk, 2),
            'worst': max((cp.risk.level for cp in plan.checkpoints if cp.risk), default=Risk.LOW).label,
        },
        'geometry': [[round(lat, 5), round(lon, 5)] for lat, lon in simplify(route.coords)],
        'checkpoints': [checkpoint_json(cp) for cp in plan.checkpoints],
    }


def checkpoint_json(cp):
    wx, assessment = cp.weather, cp.risk
    return {
        'lat': round(cp.lat, 5),
        'lon': round(cp.lon, 5),
        'mile': round(cp.mile, 1),
        'eta': cp.eta,
        'covers_mi': round(cp.covers_mi, 2),
        'weather': wx and {'wind_mph': wx.wind_mph, 'rain_in': wx.rain_in, 'snow_in': wx.snow_in},
        'risk': assessment
        and {
            'level': assessment.level.label,
            'score': int(assessment.level),
            'wind': assessment.wind.label,
            'rain': assessment.rain.label,
            'snow': assessment.snow.label,
            'load_raised': assessment.load_raised,
        },
    }
