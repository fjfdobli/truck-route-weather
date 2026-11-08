from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import routing
from common.http import ProviderError


@api_view(['GET'])
def health(request):
    return Response({'ok': True})


@api_view(['GET'])
def geocode(request):
    try:
        places = routing.search(request.query_params.get('q', ''))
    except ProviderError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
    return Response([{'label': p.label, 'lat': p.lat, 'lon': p.lon} for p in places])
