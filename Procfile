web: gunicorn jkm.wsgi
worker: celery -A jkm worker --loglevel=info --concurrency=1 --beat
release: python manage.py migrate