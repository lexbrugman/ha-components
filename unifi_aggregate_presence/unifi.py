from pyunifi.controller import Controller as BaseUnifiClient


class UnifiClient(BaseUnifiClient):
    def _logout(self):
        try:
            super(UnifiClient, self)._logout()
        except ValueError:
            pass

    def get_wireless_clients(self):
        return filter(lambda c: not c.get("is_wired", True), self.get_clients())
