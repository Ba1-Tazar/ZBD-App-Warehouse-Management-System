import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from tortoise import Tortoise

from inventory.model import Supplier, Location, Product
from user.auth import get_current_user
from user.model import User


TEST_DATABASE_URL = "postgres://baltazar:admin@localhost:5432/warehouse_test"

# MOCK: Zastępuje prawdziwe logowanie w testach
async def skip_auth():
    return User(
        username="test_admin",
        is_admin=True
    )

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    # Inicjalizacja bazy
    await Tortoise.init(
        db_url=TEST_DATABASE_URL,
        modules={"models": ["user.model", "inventory.model"]}
    )
    await Tortoise.generate_schemas()
    
    # Override autoryzacji
    app.dependency_overrides[get_current_user] = skip_auth

    yield

    # Czyszczenie wszystkich tabel po teście
    for model in Tortoise.apps.get("models").values():
        await model.all().delete()

    app.dependency_overrides = {}
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_create_product_validation_error():
    payload = {
        "name": "Invalid Product",
        "sku": "ERR-001",
        "price": -10.00,
        "stock_quantity": 5,
        "supplier_id": 1,
        "location_id": 1
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/inventory/products", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_product_success():
    # Tworzymy rekordy nadrzędne
    supplier = await Supplier.create(name="Test Supplier", contact_email="test@example.com")
    location = await Location.create(zone_name="A", shelf_number=10)

    payload = {
        "name": "Valid Keyboard",
        "sku": "OK-SKU-123",
        "price": 150.00,
        "stock_quantity": 20,
        "supplier_id": supplier.id,
        "location_id": location.id
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/inventory/products", json=payload)

    assert response.status_code == 201

    # Pobieramy produkt z relacjami
    product = await Product.get(id=response.json()["id"])
    await product.fetch_related("supplier", "location")

    data = response.json()
    assert data["name"] == "Valid Keyboard"
    assert data["sku"] == "OK-SKU-123"
    assert data["supplier"]["name"] == "Test Supplier"
    assert data["location"]["zone_name"] == "A"
