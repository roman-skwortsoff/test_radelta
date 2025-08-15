from httpx import AsyncClient
import pytest


@pytest.mark.dependency(name="add_package")
async def test_add_package_api(setup_package_type: int, api_client: AsyncClient):
    name = "тестовая посылка"
    kg = 0.58975
    usd = 0.89
    id = setup_package_type

    response = await api_client.post(
        "/packages/",
        json={"name": name, "weight_kg": kg, "value_usd": usd, "type_id": id},
    )
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)

    pytest.package_id = data["id"]


@pytest.mark.dependency(depends=["add_package"])
async def test_get_packages_api(api_client: AsyncClient):
    response = await api_client.get("/packages/")
    assert response.status_code == 200
    packages = response.json()
    assert len(packages) > 0
    assert any(p["id"] == pytest.package_id for p in packages)

    response = await api_client.get(f"/packages/{pytest.package_id}")
    assert response.status_code == 200
    package = response.json()
    assert package["id"] == pytest.package_id
