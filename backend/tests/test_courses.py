import pytest
from httpx import AsyncClient


def assert_course_response_shape(course: dict):
    assert "id" in course
    assert "title" in course
    assert "description" in course
    assert "created_at" in course
    assert "updated_at" in course
    assert "module_count" in course
    assert course["module_count"] == 0


@pytest.fixture
async def user_headers(client: AsyncClient, auth_headers):
    username = "course_test_user"
    password = "password123"
    email = "course_test_user@example.com"

    #create user admin only endpoint
    create_resp = await client.post(
        "/api/users",
        json = {"username": username, "email": email, "password": password, "role": "user"},
        headers = auth_headers,
    )

    # 201 = created, 400 = already exists
    assert create_resp.status_code in (201, 400), create_resp.text

    login_resp = await client.post(
        "/api/auth/login",
        json = {"username": username, "password": password},
    )
    assert login_resp.status_code == 200, login_resp.text
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_courses_requires_auth(client: AsyncClient):
    resp = await client.get("/api/courses")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_courses_success_as_admin(client: AsyncClient, auth_headers):
    resp = await client.get("/api/courses", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)

    for c in data:
        assert_course_response_shape(c)


@pytest.mark.asyncio
async def test_get_courses_success_as_user(client: AsyncClient, user_headers):
    resp = await client.get("/api/courses", headers=user_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)

    for c in data:
        assert_course_response_shape(c)


@pytest.mark.asyncio
async def test_get_course_by_id_requires_auth(client: AsyncClient):
    resp = await client.get("/api/courses/1")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_course_by_id_not_found(client: AsyncClient, user_headers):
    resp = await client.get("/api/courses/999999", headers=user_headers)
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Course not found"


@pytest.mark.asyncio
async def test_get_course_by_id_success_returns_modules_empty_list(client: AsyncClient, auth_headers, user_headers):
    create_resp = await client.post(
        "/api/courses",
        json = {"title": "Course for Get By ID", "description": "x"},
        headers = auth_headers,
    )
    assert create_resp.status_code == 201, create_resp.text
    course_id = create_resp.json()["id"]

    #authenticated user can GET /api/courses/{id} in the implementation
    resp = await client.get(f"/api/courses/{course_id}", headers = user_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert_course_response_shape(data)
    assert "modules" in data
    assert data["modules"] == []


@pytest.mark.asyncio
async def test_get_course_by_id_invalid_identifier_422(client: AsyncClient, user_headers):
    resp = await client.get("/api/courses/abcdefg", headers = user_headers)
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_create_course_requires_auth(client: AsyncClient):
    resp = await client.post("/api/courses", json={"title": "X"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_course_success_as_user(client: AsyncClient, user_headers):
    resp = await client.post(
        "/api/courses",
        json = {"title": "User Created Course", "description": "ok"},
        headers = user_headers,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert_course_response_shape(data)


@pytest.mark.asyncio
async def test_create_course_invalid_body_422(client: AsyncClient, auth_headers):
    resp = await client.post("/api/courses", json = {}, headers = auth_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_course_success_admin_201_and_strips_fields(client: AsyncClient, auth_headers):
    payload = {"title": "  My New Course  ", "description": "  Hello  "}
    resp = await client.post("/api/courses", json = payload, headers = auth_headers)
    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert_course_response_shape(data)
    assert data["title"] == "My New Course"
    assert data["description"] == "Hello"


@pytest.mark.asyncio
async def test_update_course_requires_auth(client: AsyncClient):
    resp = await client.patch("/api/courses/1", json={"title": "Updated"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_course_success_as_user(client: AsyncClient, auth_headers, user_headers):
    create_resp = await client.post(
        "/api/courses",
        json = {"title": "User Patch Target", "description": "x"}, 
        headers = auth_headers
    )
    assert create_resp.status_code == 201, create_resp.text
    course_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/courses/{course_id}",
        json = {"title": "User Patched"},
        headers = user_headers
    )
    assert patch_resp.status_code == 200, patch_resp.text
    data = patch_resp.json()
    assert_course_response_shape(data)
    assert data ["title"] == "User Patched"


@pytest.mark.asyncio
async def test_update_course_not_found(client: AsyncClient, auth_headers):
    resp = await client.patch("/api/courses/999999", json = {"title": "Updated"}, headers = auth_headers)
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Course not found"


@pytest.mark.asyncio
async def test_update_course_success_admin_empty_description_becomes_none(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/courses",
        json = {"title": "Temp Course", "description": "Temp"},
        headers = auth_headers,
    )
    assert create_resp.status_code == 201
    course_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/courses/{course_id}",
        json = {"title": "  Updated Title  ", "description": ""},
        headers = auth_headers,
    )
    assert patch_resp.status_code == 200, patch_resp.text
    data = patch_resp.json()

    assert_course_response_shape(data)
    assert data["title"] == "Updated Title"
    assert data["description"] is None


@pytest.mark.asyncio
async def test_update_course_invalid_body_422(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/courses",
        json = {"title": "Patch Invalid Body", "description": "x"},
        headers = auth_headers
    )
    assert create_resp.status_code == 201
    course_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/courses/{course_id}",
        json = {"title": 7, "description": ["bad"]},
        headers = auth_headers
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_delete_course_requires_auth(client: AsyncClient):
    resp = await client.delete("/api/courses/1")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_course_success_as_user(client: AsyncClient, auth_headers, user_headers):
    create_resp = await client.post(
        "/api/courses",
        json = {"title": "User Delete Target", "description": "x"},
        headers = auth_headers
    )
    assert create_resp.status_code == 201, create_resp.text
    course_id = create_resp.json()["id"]
    #forbidden as non admin
    del_resp = await client.delete(f"/api/courses/{course_id}", headers = user_headers)
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/api/courses/{course_id}", headers = user_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_course_not_found(client: AsyncClient, auth_headers):
    resp = await client.delete("/api/courses/999999", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Course not found"


@pytest.mark.asyncio
async def test_delete_course_success_admin_204_and_course_gone(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/courses",
        json={"title": "Delete Me", "description": None},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    course_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/courses/{course_id}", headers=auth_headers)
    assert del_resp.status_code == 204
    assert del_resp.text == ""

    get_resp = await client.get(f"/api/courses/{course_id}", headers=auth_headers)
    assert get_resp.status_code == 404


