[![CircleCI](https://circleci.com/gh/kflavin/stock_screener_web/tree/master.svg?style=svg)](https://circleci.com/gh/kflavin/stock_screener_web/tree/master)

# deploy to heroku
```bash
git push heroku master
heroku ps:scale web=1
```

# Dryscrape on Ubuntu
Ensure webkit dev installed
```bash
sudo apt-get install libqtwebkit-dev
```

# Tests
```bash
python manage.py tests
```

# Configure (using virtualenvwrapper)
```bash
mkvirtualenv stocks_web
pip install -r requirements.txt
```

# source environment
[Use SQLAlchemy database URI's](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls)
```bash
# Setup database URI
export DEV_DATABASE_URL="sqlite:///stocks-dev.db"
export TEST_DATABASE_URL="sqlite:///stocks-test.db"
export DATABASE_URL="sqlite:///stocks-prod.db"

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

# Create postgres table
```postgres
create user dev_user with password 'password';
create database dev_db owner dev_user;
grant all privileges on database dev_db to dev_user;
```

# setup db for local testing
```bash
python manage.py create_db
python manage.py create_admin
python manage.py runserver
```
