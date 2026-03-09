#!/bin/bash
# redis-server
# nohup celery -A chowbuddies worker --loglevel=debug &
nohup celery -A chowbuddies worker --loglevel=debug --pool=solo -Q celery &