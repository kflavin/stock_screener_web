#!/bin/bash
#echo "hello world" >> /app/myfile
#echo `pwd` >> /app/myfile
( gunicorn manage:app & )
ps -ef | grep gunicorn
cd stocks-cli/dist; python -m SimpleHTTPServer $PORT
