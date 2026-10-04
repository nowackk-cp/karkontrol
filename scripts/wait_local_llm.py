"""Bounded health wait used by CI; no model success inferred from TCP alone."""

import time
import urllib.error
import urllib.request

for attempt in range(60):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8081/health", timeout=2) as response:
            if response.status == 200:
                print("Model health ready")
                break
    except OSError:
        pass
    time.sleep(1)
else:
    raise SystemExit("Model health unavailable after 60 attempts")
