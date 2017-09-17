#!/bin/bash
#echo "hello world" >> /app/myfile
#echo `pwd` >> /app/myfile
#gunicorn manage:app

cd stocks-cli/dist; python -m SimpleHTTPServer $PORT
