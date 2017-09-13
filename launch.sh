#!/bin/bash
echo "hello world" >> /app/myfile
echo `pwd` >> /app/myfile
gunicorn manage:app
