import json
import threading
import urllib.request
import urllib.error

SERVER_URL = 'http://localhost:7823'


class OpenJCKClient:
    def __init__(self, server: str = SERVER_URL):
        self.server = server.rstrip('/')
        self._available = None  # None = not yet tested

    def _check_server(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            urllib.request.urlopen(f'{self.server}/api/health', timeout=0.3)
            self._available = True
        except Exception:
            self._available = False
        return self._available

    def _post(self, path: str, data: dict):
        try:
            body = json.dumps(data).encode()
            req = urllib.request.Request(
                f'{self.server}{path}',
                data=body,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            urllib.request.urlopen(req, timeout=0.1)
        except Exception:
            pass  # Fire and forget — never crash the agent

    def emit_run_start(self, data: dict):
        if not self._check_server():
            return
        threading.Thread(target=self._post, args=('/v1/run/start', data), daemon=True).start()

    def emit_step(self, data: dict):
        if not self._check_server():
            return
        threading.Thread(target=self._post, args=('/v1/run/step', data), daemon=True).start()

    def emit_run_end(self, data: dict):
        if not self._check_server():
            return
        threading.Thread(target=self._post, args=('/v1/run/end', data), daemon=True).start()


# Global singleton
_client = OpenJCKClient()


def get_client() -> OpenJCKClient:
    return _client
