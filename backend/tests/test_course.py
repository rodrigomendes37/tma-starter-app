"""
Contract-level tests for the /api/courses endpoint
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_courses_auth(client: AsyncClient):
    """Test that GET /api/courses requires authentication"""
    response = await client.get("/api/courses")
    assert response.status_code == 401


# split auth_headers into
@pytest.mark.asyncio
async def test_get_all_courses_with_admin_auth(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test GET /api/courses with admin role while authenticated"""
    response = await client.get(
        "/api/courses",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # verify the list contains at least 1 course
    assert len(data) >= 1

    # verify the created course contains the required fields
    for course in data:
        assert "id" in course
        assert "title" in course
        assert "description" in course
        assert "created_at" in course
        assert "updated_at" in course
        assert "module_count" in course


@pytest.mark.asyncio
async def test_get_all_us_courses_with_no_admin_auth(
    client: AsyncClient, user_auth_headers
):
    """Test GET /api/courses without admin role while authenticated"""
    response = await client.get(
        "/api/courses",
        headers=user_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # verify the list contains no courses bc lack of auth
    assert data == []

@pytest.mark.asyncio
async def test_get_course_by_id_requires_auth(client, create_course):
    """Test GET /api/courses/{course_id} without authenticated"""
    response = await client.get(f"/api/courses/{create_course.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_course_by_valid_id(client: AsyncClient, auth_headers, admin_user, create_course):
    """Test GET /api/courses/{course_id} while authenticated"""
    response = await client.get(
        f"/api/courses/{create_course.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    # verify the data is returned as a dict
    assert isinstance(data, dict)

    # verify the created course contains the required fields, and the fields are correct for the specific course
    
    assert data["id"] == create_course.id
    assert data["title"] == create_course.title
    assert data["description"] == create_course.description
    assert data["modules"] == []
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_get_course_by_invalid_id(client: AsyncClient, auth_headers, admin_user, create_course):
    """Test GET /api/courses/{course_id} while authenticated"""
    response = await client.get(
        "/api/courses/0",
        headers=auth_headers,
    )
    #test if error code thrown by endpoint is the one expected 
    assert response.status_code == 404