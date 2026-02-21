# Restful Booker API Test Project

Проект автоматизации тестирования API для [Restful Booker](https://restful-booker.herokuapp.com/) - учебного REST API для управления бронированиями отелей.

## Описание

Проект содержит автоматизированные тесты для проверки основных операций API:
- Получение списка всех бронирований
- Получение бронирования по ID
- Создание нового бронирования
- Обновление всех полей бронирования
- Обновление одного поля бронирования
- Удаление бронирования
- Фильтрация бронирований по различным параметрам

## Технологии

- Python 3.13+
- pytest - фреймворк для тестирования
- requests - библиотека для HTTP запросов
- allure-pytest - генерация отчетов
- jsonschema - валидация JSON схем
- python-dotenv - управление переменными окружения
- black, flake8, isort - линтеры и форматтеры кода

## Структура проекта

```
restful_booker_API_project/
├── functions/
│   └── api_helper.py          # Вспомогательные функции для работы с API
├── schemas/
│   ├── get_all_booking.json   # JSON схема для списка бронирований
│   ├── get_one_booking.json   # JSON схема для одного бронирования
│   └── post_booking.json      # JSON схема для создания бронирования
├── tests/
│   └── api/
│       ├── conftest.py        # Фикстуры pytest
│       └── test_booking.py    # Тесты API
├── utils/
│   └── logger.py              # Логирование для Allure отчетов
├── .env                       # Переменные окружения (не в git)
├── pyproject.toml             # Зависимости проекта
├── pytest.ini                 # Конфигурация pytest
└── README.md                  # Документация проекта
```

## Установка

1. Клонируйте репозиторий:
```bash
git clone git@github.com:PanovaAlyona/restful_booker_API_project.git
cd restful_booker_API_project
```

2. Установите зависимости:
```bash
pip install -e .
```

3. Создайте файл `.env` в корне проекта:
```env
BASE_URL=https://restful-booker.herokuapp.com/
USER_NAME=admin
PASSWORD=password123
```

## Запуск тестов

Запуск всех тестов:
```bash
pytest tests/
```

Запуск с генерацией Allure отчета:
```bash
pytest tests/ --alluredir=allure-results
```

Просмотр Allure отчета:
```bash
allure serve allure-results
```

Запуск конкретного теста:
```bash
pytest tests/api/test_booking.py::test_create_booking
```

Запуск с подробным выводом:
```bash
pytest tests/ -v
```

## Линтеры

Проверка кода с помощью flake8:
```bash
flake8 --max-line-length 79 --ignore E203,W503,E501 functions/ tests/ utils/
```

Форматирование кода с помощью black:
```bash
black --line-length 79 --target-version py311 functions/ tests/ utils/
```

Сортировка импортов с помощью isort:
```bash
isort --profile black --multi-line 3 functions/ tests/ utils/
```

## Особенности проекта

### Логирование
Все HTTP запросы и ответы логируются в:
- Консоль и файл `test_execution.log`
- Allure отчет с прикреплением тел запросов/ответов

### Валидация схем
Все ответы API валидируются с помощью JSON схем, расположенных в папке `schemas/`


### Известные баги
Некоторые тесты помечены как `xfail` из-за известных багов API:
- Фильтрация по дате checkin работает нестабильно
- Фильтрация по дате checkout не работает корректно
- Фильтрация по нескольким параметрам одновременно не работает




