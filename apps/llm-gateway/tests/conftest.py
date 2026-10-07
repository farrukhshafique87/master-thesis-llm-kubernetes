import os

# The module-level app in app.main reads settings at import time.
os.environ.setdefault("API_KEY", "import-time-key-0123456789")
