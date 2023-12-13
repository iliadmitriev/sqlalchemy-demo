import pytest


@pytest.mark.asyncio
async def test_get_user_401(get_client):
    """Тест получения пользователя без авторизации."""
    response = await get_client.get("/user/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_200(add_some_users, get_client):
    """Тест получения пользователя."""
    response = await get_client.get("/user/1", headers={"Authorization": "user1"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "user1", "login": "user1"}


@pytest.mark.asyncio
async def test_get_user_404(add_some_users, get_client):
    """Тест получения несуществующего пользователя."""
    response = await get_client.get("/user/5", headers={"Authorization": "user1"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_user(add_some_users, get_client):
    """Тест создания пользователя."""
    response = await get_client.post(
        "/user",
        headers={"Authorization": "user1"},
        json={"name": "Jimmi Hendrix", "login": "jimmihendrix"},
    )
    assert response.status_code == 200
    data = response.json()
    data.pop("id")
    assert data == {"name": "Jimmi Hendrix", "login": "jimmihendrix"}
