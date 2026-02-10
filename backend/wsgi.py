try:
	from .app import app
except ImportError:
	from app import app

# WSGI entrypoint for production servers like gunicorn
