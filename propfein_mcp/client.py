"""HTTP client for the Propfein API.

Standard library only, so the tools can be tested without installing anything.
Two settings, both read from the environment (or a local .env):

    PROPFEIN_API_URL   base URL of the API, or the word "mock" for built-in sample data
    PROPFEIN_API_KEY   the API key (sent as "Authorization: Bearer <key>")

The key is never printed, logged or put in an error message.
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MOCK_FILE = Path(__file__).with_name("mock_data.json")
TIMEOUT_SECONDS = 20


class ApiError(Exception):
    """The API answered with an error (or could not be reached)."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.status = status
        self.code = code
        self.message = message


def _clean(params: dict | None) -> dict:
    """Drop empty values and turn True/False into the words the API expects."""
    out = {}
    for k, v in (params or {}).items():
        if v is None or v == "":
            continue
        out[k] = ("true" if v else "false") if isinstance(v, bool) else v
    return out


class PropfeinClient:
    """GET-only client: this server can read the API and nothing else."""

    def __init__(self, base_url: str, api_key: str = "", opener=None):
        self.mock = base_url.strip().lower() == "mock"
        self.base_url = base_url.rstrip("/")
        self._key = api_key
        self._open = opener or urllib.request.urlopen
        if not self.mock and not self.base_url.startswith("https://"):
            raise ValueError("PROPFEIN_API_URL must start with https:// (or be the word mock)")

    @classmethod
    def from_env(cls) -> "PropfeinClient":
        try:
            from dotenv import load_dotenv
            # the repo's own .env, wherever the server was started from
            load_dotenv(Path(__file__).resolve().parent.parent / ".env")
        except ImportError:  # python-dotenv is optional here
            pass
        url = os.environ.get("PROPFEIN_API_URL", "")
        if not url:
            raise SystemExit("PROPFEIN_API_URL is not set. Copy .env.example to .env and fill it in.")
        key = os.environ.get("PROPFEIN_API_KEY", "")
        if url.strip().lower() != "mock" and not key:
            raise SystemExit("PROPFEIN_API_KEY is not set. Copy .env.example to .env and fill it in.")
        return cls(url, key)

    def get(self, path: str, params: dict | None = None) -> dict:
        """Return the API's `data` for one GET. Raises ApiError on any failure."""
        params = _clean(params)
        if self.mock:
            return self._mock(path)

        url = self.base_url + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, method="GET", headers={
            "authorization": f"Bearer {self._key}",
            "accept": "application/json",
        })
        try:
            with self._open(request, timeout=TIMEOUT_SECONDS) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise self._error(e.code, e.read()) from None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            raise ApiError(0, "unreachable", "could not reach the Propfein API") from None
        if not isinstance(body, dict) or "data" not in body:
            raise ApiError(502, "bad_answer", "the Propfein API sent an answer with no data")
        return body["data"]

    @staticmethod
    def _error(status: int, raw: bytes) -> ApiError:
        try:
            err = json.loads(raw.decode("utf-8"))["error"]
            return ApiError(status, str(err["code"]), str(err["message"]))
        except Exception:
            return ApiError(status, "http_error", f"the Propfein API answered {status}")

    def _mock(self, path: str) -> dict:
        data = json.loads(MOCK_FILE.read_text(encoding="utf-8"))
        key = "/v1/picks/{id}" if path.startswith("/v1/picks/") else path
        if key not in data:
            raise ApiError(404, "not_found", "no such route in the sample data")
        return data[key]
