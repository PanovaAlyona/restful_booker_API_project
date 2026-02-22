import json
import logging
import os
import sys
from urllib.parse import urljoin

import allure
import pytest
import requests
from dotenv import load_dotenv
from jsonschema import validate

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

from functions.api_helper import (  # noqa: E402
    change_all_fields_in_booking,
    change_one_fields_in_booking,
    create_booking,
    create_token_to_auth,
    create_url_to_get_booking_by_id,
    delete_booking,
    get_booking_by_id,
    get_id_new_booking,
)
from models.booking import Booking, BookingDates  # noqa: E402
from utils.logger import response_attaching, response_logging  # noqa: E402

logger = logging.getLogger(__name__)

load_dotenv()
URL = os.getenv("URL")
user_name = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")


@allure.feature("Booking API")
@allure.story("Получение всех бронирований")
def test_get_all_booking(get_base_url):
    with allure.step("Отправка GET запроса для получения всех бронирований"):
        url = urljoin(get_base_url, "booking")
        response = requests.get(url)
        response_logging(response)
        response_attaching(response)

    with allure.step("Проверка статус кода 200"):
        assert response.status_code == 200

    with allure.step("Валидация схемы ответа"):
        with open("schemas/get_all_booking.json") as file:
            schema = json.load(file)
            validate(instance=response.json(), schema=schema)


@allure.feature("Booking API")
@allure.story("Получение бронирования по ID")
def test_get_booking_by_id(get_base_url):
    with allure.step("Получение списка всех бронирований"):
        url = urljoin(get_base_url, "booking")
        response = requests.get(url)
        response_logging(response)
        response_attaching(response)
        bookings = response.json()
        assert len(bookings) > 0, "Список бронирований пуст"

    with allure.step("Получение ID первого бронирования"):
        first_booking_id = bookings[0]["bookingid"]
        allure.attach(
            str(first_booking_id),
            name="Booking ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        url_booking_id = create_url_to_get_booking_by_id(
            get_base_url, first_booking_id
        )

    with allure.step("Получение бронирования по ID"):
        response = get_booking_by_id(url_booking_id)

    with allure.step("Проверка статус кода 200"):
        assert response.status_code == 200

    with allure.step("Валидация схемы ответа"):
        with open("schemas/get_one_booking.json") as file:
            schema = json.load(file)
            validate(instance=response.json(), schema=schema)


@allure.feature("Booking API")
@allure.story("Создание нового бронирования")
def test_create_booking(get_base_url):
    with allure.step("Подготовка данных для создания бронирования"):
        url = urljoin(get_base_url, "booking")
        booking = Booking(
            firstname="Jim",
            lastname="Brown",
            totalprice=111,
            depositpaid=True,
            bookingdates=BookingDates(
                checkin="2018-01-01", checkout="2019-01-01"
            ),
            additionalneeds="Breakfast",
        )

    with allure.step("Создание нового бронирования"):
        response = create_booking(url, booking)

    with allure.step("Проверка статус кода 200"):
        assert response.status_code == 200

    with allure.step("Валидация схемы ответа"):
        with open("schemas/post_booking.json") as file:
            schema = json.load(file)
            validate(instance=response.json(), schema=schema)

    with allure.step("Проверка созданного бронирования"):
        new_booking_id = get_id_new_booking(response)
        allure.attach(
            str(new_booking_id),
            name="New Booking ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        url_booking_id = create_url_to_get_booking_by_id(url, new_booking_id)
        response = get_booking_by_id(url_booking_id)
        assert (
            response.json() == booking.model_dump()
        ), "Данные в бронировании не соответствует данным при создании"


@allure.feature("Booking API")
@allure.story("Фильтрация бронирований")
@pytest.mark.parametrize(
    "firstname, lastname, checkin, checkout",
    [
        ("Josh", None, None, None),
        (None, "Smith", None, None),
        pytest.param(
            None,
            None,
            "2023-06-10",
            None,
            marks=pytest.mark.xfail(
                reason="Плавающий баг с фильтром по checkin"
            ),
        ),
        pytest.param(
            None,
            None,
            None,
            "2025-01-10",
            marks=pytest.mark.xfail(reason="Баг с фильтром по checkout"),
        ),
        pytest.param(
            "Jim",
            "Brown",
            None,
            None,
            marks=pytest.mark.xfail(
                reason="Баг с фильтром по нескольким параметрам"
            ),
        ),
    ],
)
def test_get_booking_by_filter(
    get_base_url, firstname, lastname, checkin, checkout
):
    with allure.step("Формирование параметров фильтрации"):
        filter = ""
        if firstname is not None:
            filter += f"firstname={firstname}"
        if lastname is not None:
            filter += f"lastname={lastname}"
        if checkin is not None:
            filter += f"checkin={checkin}"
        if checkout is not None:
            filter += f"checkout={checkout}"
        allure.attach(
            filter, name="Filter", attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Получение бронирований с фильтром"):
        url = urljoin(get_base_url, f"booking?{filter}")
        response = requests.get(url)
        response_logging(response)
        response_attaching(response)

    with allure.step("Проверка статус кода 200"):
        assert response.status_code == 200

    with allure.step("Валидация схемы ответа"):
        with open("schemas/get_all_booking.json") as file:
            schema = json.load(file)
            validate(instance=response.json(), schema=schema)

    with allure.step("Получение деталей первого бронирования"):
        bookings = response.json()
        assert len(bookings) > 0, "Список бронирований пуст"
        first_booking_id = bookings[0]["bookingid"]

        url_booking_id = create_url_to_get_booking_by_id(
            get_base_url, first_booking_id
        )

        response = get_booking_by_id(url_booking_id)
        booking_detail = response.json()

    with allure.step("Проверка соответствия фильтрам"):
        if firstname is not None:
            assert (
                "firstname" in booking_detail
            ), "Поле firstname отсутствует в ответе"
            assert booking_detail["firstname"] == firstname

        if lastname is not None:
            assert (
                "lastname" in booking_detail
            ), "Поле lastname отсутствует в ответе"
            assert booking_detail["lastname"] == lastname

        if checkin is not None:
            assert (
                "bookingdates" in booking_detail
            ), "Поле bookingdates отсутствует в ответе"
            assert booking_detail["bookingdates"]["checkin"] >= checkin

        if checkout is not None:
            assert (
                "bookingdates" in booking_detail
            ), "Поле bookingdates отсутствует в ответе"
            assert booking_detail["bookingdates"]["checkout"] >= checkout, (
                f"Результат фильтрации по checkout = "
                f"{checkout} некорректный"
            )


@allure.feature("Booking API")
@allure.story("Обновление всех полей бронирования")
def test_update_all_fields_in_booking(get_base_url):
    with allure.step("Подготовка данных для создания бронирования"):
        url = urljoin(get_base_url, "booking")
        booking_for_create = Booking(
            firstname="Jim",
            lastname="Brown",
            totalprice=111,
            depositpaid=True,
            bookingdates=BookingDates(
                checkin="2018-01-01", checkout="2019-01-01"
            ),
            additionalneeds="Breakfast",
        )
        booking_with_change = Booking(
            firstname="Jim-Josef",
            lastname="Brown-Smith",
            totalprice=222,
            depositpaid=False,
            bookingdates=BookingDates(
                checkin="2018-05-01", checkout="2019-05-01"
            ),
            additionalneeds="Breakfast and wc in room",
        )

    with allure.step("Создание нового бронирования"):
        new_booking = create_booking(url, booking_for_create)
        id_booking = get_id_new_booking(new_booking)
        allure.attach(
            str(id_booking),
            name="Created Booking ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        url_booking_id = create_url_to_get_booking_by_id(url, id_booking)

    with allure.step("Получение токена авторизации"):
        url_auth = urljoin(get_base_url, "auth")
        token = create_token_to_auth(url_auth, user_name, password)

    with allure.step("Обновление всех полей бронирования"):
        change_all_fields_in_booking(token, url_booking_id, booking_with_change)

    with allure.step("Проверка обновленного бронирования"):
        update_booking = get_booking_by_id(url_booking_id)
        assert update_booking.json() == booking_with_change.model_dump()


@allure.feature("Booking API")
@allure.story("Обновление одного поля бронирования")
def test_update_one_fields_in_booking(get_base_url):
    with allure.step("Подготовка данных для создания бронирования"):
        url = urljoin(get_base_url, "booking")
        booking_for_create = Booking(
            firstname="Jim",
            lastname="Brown",
            totalprice=111,
            depositpaid=True,
            bookingdates=BookingDates(
                checkin="2018-01-01", checkout="2019-01-01"
            ),
            additionalneeds="Breakfast",
        )
        field_with_change = {"additionalneeds": "Nothing"}

    with allure.step("Создание нового бронирования"):
        new_booking = create_booking(url, booking_for_create)
        id_booking = get_id_new_booking(new_booking)
        allure.attach(
            str(id_booking),
            name="Created Booking ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        url_booking_id = create_url_to_get_booking_by_id(url, id_booking)

    with allure.step("Получение токена авторизации"):
        url_auth = urljoin(get_base_url, "auth")
        token = create_token_to_auth(url_auth, user_name, password)

    with allure.step("Обновление поля additionalneeds"):
        change_one_fields_in_booking(token, url_booking_id, field_with_change)

    with allure.step("Проверка обновленного поля"):
        update_booking = get_booking_by_id(url_booking_id)
        assert (
            update_booking.json()["additionalneeds"]
            == field_with_change["additionalneeds"]
        )


@allure.feature("Booking API")
@allure.story("Удаление бронирования")
def test_delete_booking(get_base_url):
    with allure.step("Подготовка данных для создания бронирования"):
        url = urljoin(get_base_url, "booking")
        booking_for_create = Booking(
            firstname="Jim",
            lastname="Brown",
            totalprice=111,
            depositpaid=True,
            bookingdates=BookingDates(
                checkin="2018-01-01", checkout="2019-01-01"
            ),
            additionalneeds="Breakfast",
        )

    with allure.step("Создание нового бронирования"):
        new_booking = create_booking(url, booking_for_create)
        id_booking = get_id_new_booking(new_booking)
        allure.attach(
            str(id_booking),
            name="Created Booking ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        url_booking_id = create_url_to_get_booking_by_id(url, id_booking)

    with allure.step("Получение токена авторизации"):
        url_auth = urljoin(get_base_url, "auth")
        token = create_token_to_auth(url_auth, user_name, password)

    with allure.step("Удаление бронирования"):
        delete_booking(token, url_booking_id)

    with allure.step("Проверка что бронирование удалено (статус 404)"):
        booking = get_booking_by_id(url_booking_id)
        assert booking.status_code == 404
