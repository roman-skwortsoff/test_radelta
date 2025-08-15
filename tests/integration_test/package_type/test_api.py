from httpx import AsyncClient
import pytest


@pytest.mark.parametrize(
    "title, status_code",
    [
        ("тест1", 201),
        ("тест2", 201),
        ("тест1", 409),
    ],
)
async def test_add_package_types_api(
    api_client: AsyncClient, title: str, status_code: int
):
    response = await api_client.post(
        "/package_types/",
        json={"name": title},
    )
    assert response.status_code == status_code


async def test_get_package_types_api(api_client: AsyncClient):
    response = await api_client.get("/package_types/")
    assert response.status_code == 200
