#!/bin/bash

pkill -f celery
pkill -f runserver

screen -mdS run python manage.py runserver

celery -A ChatBox purge -f
screen -mdS send-sms celery -A ChatBox worker -Q send_sms -n send_sms.@%h -f ./log/python/celery/send_sms.log --concurrency=1 -l debug