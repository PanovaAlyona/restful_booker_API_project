import json
import logging

import allure
from allure_commons.types import AttachmentType
from requests import Response


def setup_logging():
    """Настройка базового логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("test_execution.log"),
            logging.StreamHandler(),
        ],
    )


def response_logging(response: Response):
    """Логирование ответа API в консоль и файл"""
    logging.info("Request: " + response.request.url)
    if response.request.body:
        logging.info("INFO Request body: " + str(response.request.body))
    logging.info("Request headers: " + str(response.request.headers))
    logging.info("Response code " + str(response.status_code))
    logging.info("Response: " + response.text)


def response_attaching(response: Response):
    """Прикрепление информации о запросе/ответе в Allure"""
    allure.attach(
        body=response.request.url,
        name="Request url",
        attachment_type=AttachmentType.TEXT,
    )

    if response.request.body:
        try:
            if isinstance(response.request.body, dict):
                body_data = response.request.body
            else:
                body_data = json.loads(response.request.body)

            allure.attach(
                body=json.dumps(body_data, indent=4, ensure_ascii=True),
                name="Request body",
                attachment_type=AttachmentType.JSON,
                extension="json",
            )
        except Exception:
            allure.attach(
                body=str(response.request.body),
                name="Request body",
                attachment_type=AttachmentType.TEXT,
            )

    try:
        allure.attach(
            body=json.dumps(response.json(), indent=4, ensure_ascii=True),
            name="Response",
            attachment_type=AttachmentType.JSON,
            extension="json",
        )
    except Exception:
        allure.attach(
            body=response.text,
            name="Response",
            attachment_type=AttachmentType.TEXT,
        )


def attach_screenshot(name="screenshot"):
    """Прикрепление скриншота в Allure"""
    try:
        from selene import browser

        allure.attach(
            browser.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=AttachmentType.PNG,
        )
    except Exception as e:
        logging.error(f"Не удалось сделать скриншот: {e}")


def attach_html(name="page_html"):
    """Прикрепление HTML страницы в Allure"""
    try:
        from selene import browser

        html = browser.driver.page_source
        allure.attach(html, name=name, attachment_type=AttachmentType.HTML)
    except Exception as e:
        logging.error(f"Не удалось получить HTML: {e}")
