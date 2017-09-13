#!/bin/bash
gunicorn manage:app &
echo "hello world" >> ./file
