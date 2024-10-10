# delivery_test_task/tests/test_fastapi_routes.py
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from delivery_test_task.app.main import app
from delivery_test_task.worker.tasks import check_dollar_exchange_rate, register_parcel
from delivery_test_task.models.sqlalchemy_models import Parcel

client = TestClient(app)

@pytest.mark.asyncio
@patch("delivery_test_task.worker.tasks.check_dollar_exchange_rate_async", new_callable=AsyncMock)
@patch("delivery_test_task.worker.redis_app.redis_client.get", new_callable=AsyncMock)
async def test_check_dollar_exchange_rate(redis_mock, exchange_rate_mock):
    """
    Тест для эндпоинта /dollar-exchange-rate с моками на Redis и внешний запрос курса доллара.
    """
    redis_mock.return_value = None  # Нет данных в Redis
    exchange_rate_mock.return_value = 75.0  # Мокаем курс доллара

    response = client.get("/dollar-exchange-rate")

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data


@pytest.mark.asyncio
@patch("delivery_test_task.worker.tasks.register_parcel_async", new_callable=AsyncMock)
@patch("delivery_test_task.worker.redis_app.redis_client.get", new_callable=AsyncMock)
async def test_register_parcel(redis_mock, register_parcel_mock):
    """
    Тест для эндпоинта /parcel-registration с моками на Redis и регистрацию посылки.
    """
    redis_mock.return_value = b"75.0"  # Мокаем курс доллара в Redis
    register_parcel_mock.return_value = None  # Мокаем успешную регистрацию

    parcel_data = {
        "name": "Test Parcel",
        "weight": 2.5,
        "value": 1500,
        "parcel_type_id": 1
    }

    response = client.post("/parcel-registration", json=parcel_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data


@pytest.mark.asyncio
@patch("delivery_test_task.models.sqlalchemy_models.Parcel.get_all", new_callable=AsyncMock)
async def test_get_parcels(mock_get_all):
    """
    Тест для эндпоинта /parcels с мокированием получения списка посылок из базы данных.
    """
    mock_get_all.return_value = ([], 0)  # Пустой список посылок

    response = client.get("/parcels?page=1&page_size=10")

    assert response.status_code == 200
    data = response.json()
    assert "parcels" in data
    assert "total" in data
    assert data["parcels"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
@patch("delivery_test_task.models.sqlalchemy_models.Parcel.assign_company", new_callable=AsyncMock)
async def test_assign_company(mock_assign_company):
    """
    Тест для эндпоинта /parcels/{parcel_id}/assign-company с мокированием привязки компании к посылке.
    """
    mock_assign_company.return_value = None  # Успешная привязка компании

    response = client.post("/parcels/1/assign-company?company_id=1")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Company assigned successfully"


@pytest.mark.asyncio
@patch("delivery_test_task.models.sqlalchemy_models.Parcel.create", new_callable=AsyncMock)
async def test_create_parcel(mock_create):
    """
    Тест для создания новой посылки с мокированием добавления в базу данных.
    """
    mock_create.return_value = Parcel(id=1, name="Test Parcel", weight=2.5, value=1500, parcel_type_id=1)

    parcel_data = {
        "name": "Test Parcel",
        "weight": 2.5,
        "value": 1500,
        "parcel_type_id": 1
    }

    response = client.post("/parcel-registration", json=parcel_data)

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data


@pytest.mark.asyncio
async def test_log_requests():
    """
    Тест для middleware log_requests, который логирует каждый запрос и его тело.
    """
    with patch("delivery_test_task.app.main.logger.info") as mock_logger:
        response = client.get("/parcels")

        assert response.status_code == 200
        assert mock_logger.called


async def test_get_user_id_new_cookie():
    """
    Тест для хелпера get_user_id при создании нового user_id, если он отсутствует в cookies.
    """
    # Патчим логгер, чтобы предотвратить его использование в тесте
    with patch("delivery_test_task.app.main.logger.debug") as mock_logger:
        # Создаем новый событийный цикл для использования внутри теста
        import asyncio
        loop = asyncio.get_event_loop()

        # Используем TestClient внутри асинхронного контекста с событийным циклом
        async with TestClient(app) as client:
            # Выполняем GET запрос к эндпоинту /parcels
            response = await loop.run_in_executor(None, client.get, "/parcels")

            # Проверяем статус ответа и содержимое
            assert response.status_code == 200
            mock_logger.assert_called_once_with("Создан новый user_id и записан в cookie")
