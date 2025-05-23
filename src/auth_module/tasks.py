from celery import shared_task
import requests
from django.conf import settings
import simplejson
from rest_framework import status
import logging

logger = logging.getLogger("django")


@shared_task(queue='send-sms')
def send_sms(phone_no:str, token:str):
    url = settings.SMS_SERVICE_DOMAIN
    api_key = settings.SMS_SERVICE_API_KEY
    payload_json = {
        "OtpId": "805",
        "ReplaceToken": [str(token)],
        "MobileNumber": str(phone_no)
    }
    try:
        for i in range(3):
            request = requests.post(url=url, json=payload_json, headers={"apiKey": api_key})
            request_response = simplejson.loads(request.text)
            if request.status_code == status.HTTP_200_OK:
                if request_response["success"] is True:
                    logger.info("Sms sent successfully.")
        return logger.warning("Error sending SMS!")
    except Exception as e:
        logger.critical(f"Error sending SMS: {e}", exc_info=True)
