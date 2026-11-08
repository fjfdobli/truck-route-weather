import time

import requests
from django.conf import settings

TIMEOUT_S = 15
RETRY_DELAYS_S = (1, 3)
RETRIES = len(RETRY_DELAYS_S)
RETRY_STATUSES = {429, 500, 502, 503, 504}


class ProviderError(Exception):
    """A third-party API failed or returned something we can't use. `payload` is its JSON body, if any."""

    def __init__(self, message, payload=None):
        super().__init__(message)
        self.payload = payload or {}


_session = requests.Session()


def get_json(url, params=None, retries=RETRIES, timeout=TIMEOUT_S):
    host = url.split('/')[2]
    for attempt in range(retries + 1):
        try:
            response = _session.get(
                url,
                params=params,
                timeout=timeout,
                headers={'User-Agent': settings.HTTP_USER_AGENT},
            )
        except (requests.ConnectionError, requests.Timeout) as exc:
            if attempt < retries:
                time.sleep(RETRY_DELAYS_S[attempt])
                continue
            raise ProviderError(f'{host} did not respond. Try again shortly.') from exc

        if response.status_code in RETRY_STATUSES and attempt < retries:
            time.sleep(RETRY_DELAYS_S[attempt])
            continue
        if response.status_code == 429:
            raise ProviderError(f'{host} is busy (rate limit). Try again in a minute.')

        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderError(f'{host} returned an unreadable response ({response.status_code}).') from exc

        if not response.ok:
            # Never echo the request URL: it is noise to users and can carry keys.
            reason = data.get('message') or data.get('reason') if isinstance(data, dict) else None
            raise ProviderError(f'{host}: {reason or f"request failed ({response.status_code})"}', data)
        return data
