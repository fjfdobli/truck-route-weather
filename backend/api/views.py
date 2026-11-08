from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import planner
import routing
from common.http import ProviderError

from .presenters import place_json, trip_json
from .serializers import PlanRequestSerializer


@api_view(['GET'])
def health(request):
    return Response({'ok': True})


@api_view(['GET'])
def geocode(request):
    try:
        places = routing.search(request.query_params.get('q', ''))
    except ProviderError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
    return Response([place_json(p) for p in places])


@api_view(['POST'])
def plan(request):
    serializer = PlanRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    places, errors = {}, {}
    for field in ('origin', 'destination'):
        try:
            places[field] = _place(data[field])
        except routing.PlaceNotFound as exc:
            errors[field] = [str(exc)]
        except ProviderError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        else:
            if not routing.in_service_area(places[field]):
                errors[field] = [f'This planner covers {routing.SERVICE_AREA_NAME}.']
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    origin, destination = places['origin'], places['destination']
    try:
        trip = planner.plan_trip(origin, destination, data['departure'], data['weight_lb'], data['interval_mi'])
    except routing.NoRouteError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except ProviderError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    return Response(trip_json(trip, data, origin, destination))


def _place(data):
    if 'lat' in data:
        return routing.Place(data['label'], data['lat'], data['lon'])
    return routing.resolve(data['label'])
