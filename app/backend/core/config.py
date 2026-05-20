import os


APP_NAME = "BaliNavi Backend"
APP_VERSION = "0.1.0"
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
