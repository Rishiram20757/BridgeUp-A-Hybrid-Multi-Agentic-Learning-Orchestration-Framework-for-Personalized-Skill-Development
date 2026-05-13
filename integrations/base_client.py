import requests
from typing import Dict, Any
from .rate_limiter import RateLimiter
from .exceptions import APIError


class BaseAPIClient:

    def __init__(self, base_url: str, rate_limit_per_sec: int = 5):
        self.base_url = base_url
        self.rate_limiter = RateLimiter(rate_limit_per_sec)

    def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict:

        self.rate_limiter.wait()

        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                raise APIError(f"API returned {response.status_code}")

            return response.json()

        except requests.exceptions.RequestException as e:
            raise APIError(str(e))