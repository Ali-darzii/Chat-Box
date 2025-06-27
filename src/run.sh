#!/bin/bash

pkill -f celery
pkill -f runserver

screen -mdS run python manage.py runserver 127.0.0.1:8000

celery -A ChatBox purge -f
screen -mdS send-sms celery -A ChatBox worker -Q send_sms -n send_sms.@%h -f ./log/python/celery/send_sms.log --concurrency=1 -l debug
screen -mdS private_boxes celery -A ChatBox worker -Q private_boxes -n private_boxes.@%h -f ./log/python/celery/private_boxes.log --concurrency=1 -l debug