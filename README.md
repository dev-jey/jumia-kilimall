# Jumia-kilimall

This is a web application that implements a web scrapper to get data for products from jumia and killimall, and use linear regression to recomment the best products to clients

# Technologies used
- Django
- Beautiful soup 4
- Selenium
- Celery
- Html/css

### How To Set Up Locally
Install pipenv
```
pip install virtualenv
```

Create virtual environment
```
virtualenv -p python3 env  && source env/bin/activate
```

Install dependencies
```
pip install -r requirements.txt
```

Migrate to DB
```
python manage.py migrate
```

Load static data 
```
python manage.py loaddata sites
```

Run the server
```
python manage.py runserver
```

Run redis server
```
redis-server
```

Run celery
```
celery -A jkm worker --loglevel=info --concurrency=1 --beat
```


### Env Variables

```
export CELERY_TIME_J=*/60
export CELERY_TIME_K=*/1200
export DB_NAME=name
export DB_USER=user
export REDIS_URL=redis://127.0.0.1:6379
export CURRENT_ENV=development
```