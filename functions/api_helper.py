import logging
import sys
import os
from urllib.parse import urljoin

import requests

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from models.booking import (  # noqa: E402
    AuthCredentials,
    Booking,
    BookingResponse,
)
from utils.logger import response_attaching, response_logging  # noqa: E402

logger = logging.getLogger(__name__)


def create_booking(url, booking: Booking):
    payload = booking.model_dump()
    response = requests.post(url=url, json=payload)
    response_logging(response)
    response_attaching(response)

    BookingResponse.model_validate(response.json())
    
    return response


def get_id_new_booking(response):
    return response.json().get("bookingid")


def get_booking_by_id(url_booking_id):
    response = requests.get(url_booking_id)
    response_logging(response)
    response_attaching(response)

    if response.status_code == 200:
        Booking.model_validate(response.json())
    
    return response


def create_url_to_get_booking_by_id(url, id):
    return urljoin(url, f"booking/{id}")


def create_token_to_auth(url, user_name, password):
    credentials = AuthCredentials(username=user_name, password=password)
    response = requests.post(url=url, json=credentials.model_dump())
    response_logging(response)
    response_attaching(response)
    return response.json().get("token")


def change_all_fields_in_booking(token, url_booking_id, booking: Booking):
    cookies = {
        "token": token,
    }
    payload = booking.model_dump()
    response = requests.put(
        cookies=cookies, url=url_booking_id, json=payload
    )
    response_logging(response)
    response_attaching(response)

    Booking.model_validate(response.json())
    
    return response


def change_one_fields_in_booking(token, url_booking_id, field_with_change):
    cookies = {
        "token": token,
    }
    response = requests.patch(
        cookies=cookies, url=url_booking_id, json=field_with_change
    )
    response_logging(response)
    response_attaching(response)
    return response


def delete_booking(token, url_booking_id):
    cookies = {"token": token}
    response = requests.delete(cookies=cookies, url=url_booking_id)
    response_logging(response)
    response_attaching(response)
    return response
