import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from ..app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def db_session():
    mock_session = AsyncMock(spec=AsyncSession)
    yield mock_session

@pytest.fixture(autouse=True)
def override_db_session(db_session):
    app.dependency_overrides[AsyncSession] = lambda: db_session
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_parcel_registration(client):
    with patch('delivery_test_task.models.sqlalchemy_models.Parcel.create', return_value={"task_id": 1}):
        response = client.post(
            "/parcel-registration",
            json={
                "name": "Test Test",
                "weight": 5,
                "value": 100,
                "parcel_type_id": 1
            }
        )
        assert response.status_code == 200
        assert "task_id" in response.json()

# @pytest.mark.asyncio
# async def test_assign_company(client):
#     with patch('delivery_test_task.app.routes.assign_company', return_value={"message": "Company assigned successfully"}):
#         response = client.post("/parcels/1/assign-company?company_id=1")
#         assert response.status_code == 200
#         assert response.json() == {"message": "Company assigned successfully"}
