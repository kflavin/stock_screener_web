# deploy to heroku
git push heroku master
heroku ps:scale web=1
