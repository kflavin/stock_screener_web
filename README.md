# deploy to heroku
```bash
git push heroku master
heroku ps:scale web=1
```

# Tests
```bash
python manage.py tests
```

# Configure (using virtualenvwrapper)
```bash
mkvirtualenv stocks_web
```

# source environment
```bash
# SQLAlchemy database URI's
export DEV_DATABASE_URL="sqlite://stocks-dev.db"
export TEST_DATABASE_URL="sqlite://stocks-test.db"
export DATABASE_URL="sqlite://stocks-prod.db"

export MAIL_SENDER='youremail@example.com'
export MAIL_USER=<username>
export MAIL_PASSWORD=<password>
export SECURITY_PASSWORD_HASH="sha512_crypt"
export SECURITY_PASSWORD_SALT="somelongsaltstraing"

export PYTHONPATH=.:$PYTHONPATH

# Optional
export CLI_USER=<cli_user>
export CLI_PASSWORD=<cli_password>
export CLI_HOST=http://127.0.0.1:5000
```
