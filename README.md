# deploy to heroku
git push heroku master
heroku ps:scale web=1

# Tests
python manage.py tests
