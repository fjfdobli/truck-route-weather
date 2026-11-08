from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound
from django.urls import include, path, re_path


def frontend(request):
    """The built React app. Its files (scripts, icons) are served by WhiteNoise."""
    index = settings.FRONTEND_DIST / 'index.html'
    if not index.is_file():
        return HttpResponseNotFound('Frontend not built. Run `npm run build` in frontend/.')
    response = FileResponse(index.open('rb'), content_type='text/html')
    response['Cache-Control'] = 'no-cache'
    return response


urlpatterns = [
    path('api/', include('api.urls')),
    re_path(r'^(?!api/).*$', frontend),
]
