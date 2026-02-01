import requests

class Verifier:
    def __init__(self, config):
        self.config = config

    def check_health(self, url="http://127.0.0.1:8008/health"):
        try:
            r = requests.get(url, timeout=3)
            return {"ok": r.status_code == 200, "status": r.text}
        except Exception as e:
            return {"ok": False, "error": str(e)}
