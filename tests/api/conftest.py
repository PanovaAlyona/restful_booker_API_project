import os

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def get_base_url():
    print(os.getenv("BASE_URL"))
    return os.getenv("BASE_URL")
