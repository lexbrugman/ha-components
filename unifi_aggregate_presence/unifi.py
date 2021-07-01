import logging
import requests
from pyunifi.controller import Controller as BaseUnifiClient

_LOGGER = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 8


class DefaultTimeoutHTTPAdapter(requests.adapters.HTTPAdapter):
    def send(self, *args, **kwargs):
        if kwargs["timeout"] is None:
            kwargs["timeout"] = DEFAULT_TIMEOUT

        return super().send(*args, **kwargs)


class UnifiClient(BaseUnifiClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.session.mount("http://", DefaultTimeoutHTTPAdapter())
        self.session.mount("https://", DefaultTimeoutHTTPAdapter())

    def _logout(self):
        try:
            super()._logout()
        except ValueError:
            pass

    def get_wireless_clients(self):
        return filter(lambda c: not c.get("is_wired", True), self.get_clients())
