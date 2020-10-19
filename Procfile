web: gunicorn jkm.wsgi
worker: celery -A jkm worker --loglevel=INFO --concurrency=1 --beat
release: python manage.py migrate && python manage.py loaddata sites