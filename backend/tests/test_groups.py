"""
Contract-level tests for the /api/groups endpoint
"""

import pytest
from httpx import AsyncClient

"""Test that GET /api/groups list all accessible groups"""


# Admins and managers see all groups
@pytest.mark.asyncio
async def test_get_all_groups_admin(
    client: AsyncClient,
    auth_headers,
    admin_user,
    test_group_inaccessible_by_regular,
    test_group_accessible_by_regular,
):
    """Test that GET /api/groups list all accessible groups admin"""
    response = await client.get("/api/groups", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # At least the two test groups created

    # Verify each item in the list has the expected group structure
    for group in data:
        assert "id" in group
        assert "name" in group
        assert "description" in group
        assert "created_by" in group
        assert "created_at" in group
        assert "updated_at" in group
        assert "member_count" in group


# Regular users see only groups they're members of
@pytest.mark.asyncio
async def test_get_all_groups_regular_user(
    client: AsyncClient,
    user_auth_headers,
    regular_user,
    test_group_accessible_by_regular,
    test_group_inaccessible_by_regular,
):
    """Test that GET /api/groups list all accessible groups regular user"""
    response = await client.get("/api/groups", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1  # At least the one test group they belong to

    # Verify each item in the list has the expected group structure
    for group in data:
        assert "id" in group
        assert "name" in group
        assert "description" in group
        assert "created_by" in group
        assert "created_at" in group
        assert "updated_at" in group
        assert "member_count" in group


"""Test that GET /api/groups/{id} gets a single group with members"""


@pytest.mark.asyncio
async def test_get_group_with_id_valid_admin(
    client: AsyncClient, auth_headers, admin_user, test_group_inaccessible_by_regular
):
    """Test that GET /api/groups/{id} gets a single group with members admin"""

    # Get the specific group by ID
    response = await client.get(
        f"/api/groups/{test_group_inaccessible_by_regular.id}", headers=auth_headers
    )
    assert response.status_code == 200
    group = response.json()

    # Verify the group structure
    assert "id" in group
    assert "name" in group
    assert "description" in group
    assert "created_by" in group
    assert "created_at" in group
    assert "updated_at" in group
    assert "member_count" in group
    assert "members" in group
    assert isinstance(group["members"], list)

    # Verify each member in the group has the expected structure
    for member in group["members"]:
        assert "user_id" in member
        assert "username" in member
        assert "email" in member
        assert "role" in member
        assert "group_role" in member
        assert "user_role" in member
        assert "joined_at" in member
        assert "avatar_url" in member
        assert "first_name" in member
        assert "last_name" in member
        assert "child_dob" in member
        assert "updated_at" in member


@pytest.mark.asyncio
async def test_get_group_with_id_valid_regular_user(
    client: AsyncClient,
    user_auth_headers,
    regular_user,
    test_group_accessible_by_regular,
):
    """Test that GET /api/groups/{id} gets a single group with members regular user"""
    group_id = test_group_accessible_by_regular.id
    # Get the specific group by ID
    response = await client.get(f"/api/groups/{group_id}", headers=user_auth_headers)
    assert response.status_code == 200
    group = response.json()

    # Verify the group structure
    assert "id" in group
    assert "name" in group
    assert "description" in group
    assert "created_by" in group
    assert "created_at" in group
    assert "updated_at" in group
    assert "member_count" in group
    assert "members" in group
    assert isinstance(group["members"], list)

    # Verify each member in the group has the expected structure
    for member in group["members"]:
        assert "user_id" in member
        assert "username" in member
        assert "email" in member
        assert "role" in member
        assert "group_role" in member
        assert "user_role" in member
        assert "joined_at" in member
        assert "avatar_url" in member
        assert "first_name" in member
        assert "last_name" in member
        assert "child_dob" in member
        assert "updated_at" in member

    # Verify that user is in the group
    member_ids = [member["user_id"] for member in group["members"]]
    assert regular_user.id in member_ids


@pytest.mark.asyncio
async def test_get_group_with_id_not_found_admin(client: AsyncClient, auth_headers):
    """Test that GET /api/groups/{id} returns 404 for non-existent group admin"""
    response = await client.get("/api/groups/99999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_group_with_id_not_found_regular_user(
    client: AsyncClient, user_auth_headers, test_group_inaccessible_by_regular
):
    """Test that GET /api/groups/{id} returns 403 for an inaccessible user"""
    response = await client.get(
        f"/api/groups/{test_group_inaccessible_by_regular.id}",
        headers=user_auth_headers,
    )
    assert response.status_code == 403


async def test_get_group_with_id_non_existent_regular_user(
    client: AsyncClient, user_auth_headers, test_group_inaccessible_by_regular
):
    """Test that GET /api/groups/{id} returns 404 for non-existent group regular user"""
    response = await client.get("/api/groups/99999", headers=user_auth_headers)
    assert response.status_code == 404


async def test_get_group_with_string_id_admin(client: AsyncClient, auth_headers):
    """Test that GET /api/groups/{id} returns 422 for string id admin"""
    response = await client.get("/api/groups/invalid_id", headers=auth_headers)
    assert response.status_code == 422


"""Test that POST /api/groups creates a new group"""


@pytest.mark.asyncio
async def test_create_group_admin_valid(client: AsyncClient, auth_headers):
    """Test that POST /api/groups creates a new group by admin with valid data"""
    group_data = {
        "name": "newgroup",
        "description": "this is a new group for testing",
    }
    response = await client.post("/api/groups", json=group_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "newgroup"
    assert data["description"] == "this is a new group for testing"
    assert "id" in data

    # Verify the group was actually created by retrieving it through the API
    group_id = data["id"]
    get_response = await client.get(f"/api/groups/{group_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_group = get_response.json()
    assert retrieved_group["name"] == "newgroup"
    assert retrieved_group["description"] == "this is a new group for testing"
    assert retrieved_group["member_count"] == 1  # Creator is the first member


@pytest.mark.asyncio
async def test_create_group_admin_invalid(client: AsyncClient, auth_headers):
    """Test that POST /api/groups fails to create a new group by admin with
    missing name field"""
    group_data = {
        "description": "missing name field",
    }
    response = await client.post("/api/groups", json=group_data, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_group_admin_empty_string_name(client: AsyncClient, auth_headers):
    """Test that POST /api/groups fails to create a new group by admin with
    empty string name"""
    group_data = {
        "name": "",
        "description": "empty name field",
    }
    response = await client.post("/api/groups", json=group_data, headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_group_admin_name_not_string(client: AsyncClient, auth_headers):
    """Test that POST /api/groups fails to create a new group by admin with
    non-string name"""
    group_data = {
        "name": 123,
        "description": "name is not a string",
    }
    response = await client.post("/api/groups", json=group_data, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_group_admin_no_description(client: AsyncClient, auth_headers):
    """Test that POST /api/groups creates a new group by admin without description"""
    group_data = {
        "name": "group_without_description",
    }
    response = await client.post("/api/groups", json=group_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "group_without_description"
    assert data["description"] is None
    assert "id" in data

    # Verify the group was actually created by retrieving it through the API
    group_id = data["id"]
    get_response = await client.get(f"/api/groups/{group_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_group = get_response.json()
    assert retrieved_group["name"] == "group_without_description"
    assert retrieved_group["description"] is None
    assert retrieved_group["member_count"] == 1  # Creator is the first member


@pytest.mark.asyncio
async def test_create_group_admin_description_not_string(
    client: AsyncClient, auth_headers
):
    """Test that POST /api/groups fails to create a new group by admin
    with non-string description"""
    group_data = {
        "name": "group_with_invalid_description",
        "description": 456,
    }
    response = await client.post("/api/groups", json=group_data, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_group_regular_user_invalid(
    client: AsyncClient, user_auth_headers
):
    """Test that POST /api/groups fails to create a new group by regular
    user with no name field"""
    group_data = {
        "description": "missing name field",
    }
    response = await client.post(
        "/api/groups", json=group_data, headers=user_auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_group_regular_user_valid(client: AsyncClient, user_auth_headers):
    """Test that POST /api/groups fails to create a new group by regular user with
    valid data"""
    group_data = {
        "name": "newgroup_by_user",
        "description": "this group should not be made",
    }
    response = await client.post(
        "/api/groups", json=group_data, headers=user_auth_headers
    )
    assert response.status_code == 403


"""Test that PATCH /api/groups/{id} updates an existing group"""


@pytest.mark.asyncio
async def test_update_group_admin_valid_id(
    client: AsyncClient, auth_headers, test_group_inaccessible_by_regular
):
    """Test that PATCH /api/groups/{id} updates an existing group by admin with
    valid id"""
    group_id = test_group_inaccessible_by_regular.id
    # update the group
    update_data = {
        "name": "updated_group_name",
        "description": "updated description",
    }
    response = await client.patch(
        f"/api/groups/{group_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_group_name"
    assert data["description"] == "updated description"

    # Verify the group was actually updated by retrieving it through API
    get_response = await client.get(f"/api/groups/{group_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_group = get_response.json()
    assert retrieved_group["name"] == "updated_group_name"
    assert retrieved_group["description"] == "updated description"


@pytest.mark.asyncio
async def test_update_group_regular_user_valid_id(
    client: AsyncClient, user_auth_headers, test_group_accessible_by_regular
):
    """Test that PATCH /api/groups/{id} does not update an existing group by
    regular user with valid id"""
    group_id = test_group_accessible_by_regular.id

    # attempt to update the group
    update_data = {
        "name": "updated_group_name_by_user",
        "description": "updated description_by_user",
    }
    response = await client.patch(
        f"/api/groups/{group_id}", json=update_data, headers=user_auth_headers
    )
    assert response.status_code == 403

    # Verify the group was not updated by retrieving it through API
    get_response = await client.get(
        f"/api/groups/{group_id}", headers=user_auth_headers
    )
    assert get_response.status_code == 200
    retrieved_group = get_response.json()
    assert retrieved_group["name"] != "updated_group_name_by_user"
    assert retrieved_group["description"] != "updated description_by_user"


@pytest.mark.asyncio
async def test_update_group_admin_invalid_id(client: AsyncClient, auth_headers):
    """Test that PATCH /api/groups/{id} fails to update an existing group
    by admin with invalid id"""
    response = await client.patch(
        "/api/groups/99999", json={"name": "invalid"}, headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_group_regular_user_invalid_id(
    client: AsyncClient, user_auth_headers
):
    """Test that PATCH /api/groups/{id} fails to update an existing group by
    regular user with invalid id"""
    response = await client.patch(
        "/api/groups/99999", json={"name": "invalid"}, headers=user_auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_group_admin_name_only(
    client: AsyncClient, auth_headers, test_group_inaccessible_by_regular
):
    """Test that PATCH /api/groups/{id} updates only the name of an
    existing group by admin"""
    group_id = test_group_inaccessible_by_regular.id

    # update the group
    update_data = {
        "name": "updated_group_name",
    }
    response = await client.patch(
        f"/api/groups/{group_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_group_name"

    # Verify the group was actually updated by retrieving it through API
    get_response = await client.get(f"/api/groups/{group_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_group = get_response.json()
    assert retrieved_group["name"] == "updated_group_name"


@pytest.mark.asyncio
async def test_update_admin_description_only(
    client: AsyncClient, auth_headers, test_group_inaccessible_by_regular
):
    """Test that PATCH /api/groups/{id} updates only the description of an
    existing group by admin"""
    group_id = test_group_inaccessible_by_regular.id

    # update the group
    update_data = {
        "description": "updated_group_description",
    }
    response = await client.patch(
        f"/api/groups/{group_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "updated_group_description"

    # Verify the group was actually updated by retrieving it through API
    get_response = await client.get(f"/api/groups/{group_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_group = get_response.json()
    assert retrieved_group["description"] == "updated_group_description"


@pytest.mark.asyncio
async def test_update_group_admin_invalid_name_empty_string(
    client: AsyncClient, auth_headers, test_group_inaccessible_by_regular
):
    """Test that PATCH /api/groups/{id} fails to update an existing group by
    admin with invalid name"""
    group_id = test_group_inaccessible_by_regular.id

    # update the group
    update_data = {
        "name": "",
        "description": "updated description",
    }
    response = await client.patch(
        f"/api/groups/{group_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_group_admin_invalid_name_int(
    client: AsyncClient, auth_headers, test_group_inaccessible_by_regular
):
    """Test that PATCH /api/groups/{id} fails to update an existing group by
    admin with invalid name"""
    group_id = test_group_inaccessible_by_regular.id

    # update the group
    update_data = {
        "name": 123,
        "description": "updated description",
    }
    response = await client.patch(
        f"/api/groups/{group_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_group_admin_invalid_description(
    client: AsyncClient, auth_headers, test_group_inaccessible_by_regular
):
    """Test that PATCH /api/groups/{id} fails to update an existing group by admin
    with invalid description"""
    group_id = test_group_inaccessible_by_regular.id

    # update the group
    update_data = {
        "name": "updated_group_name",
        "description": 123,
    }
    response = await client.patch(
        f"/api/groups/{group_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_group_admin_no_params(
    client: AsyncClient, auth_headers, test_group_inaccessible_by_regular
):
    """Test that PATCH /api/groups/{id} succeeds to update and does nothing"""
    group_id = test_group_inaccessible_by_regular.id

    # update the group with no parameters
    update_data = {}
    response = await client.patch(
        f"/api/groups/{group_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200

    # Verify the group was actually unchanged by retrieving it through API
    get_response = await client.get(f"/api/groups/{group_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_group = get_response.json()
    assert retrieved_group["name"] == test_group_inaccessible_by_regular.name
    assert (
        retrieved_group["description"] == test_group_inaccessible_by_regular.description
    )


@pytest.mark.asyncio
async def test_update_group_admin_string_id(client: AsyncClient, auth_headers):
    """Test that PATCH /api/groups/{id} fails to update an existing group by
    admin with string id"""
    response = await client.patch(
        "/api/groups/invalid_id", json={"name": "invalid"}, headers=auth_headers
    )
    assert response.status_code == 422


"""Test that DELETE /api/groups/{id} deletes a group"""


@pytest.mark.asyncio
async def test_delete_group_admin_valid_id(
    client: AsyncClient, auth_headers, test_group_inaccessible_by_regular
):
    """Test that DELETE /api/groups/{id} deletes a group by admin with valid id"""
    group_id = test_group_inaccessible_by_regular.id

    # delete the group
    response = await client.delete(f"/api/groups/{group_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify the group was actually deleted by attempting to retrieve it
    get_response = await client.get(f"/api/groups/{group_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_group_regular_user_valid_id(
    client: AsyncClient, user_auth_headers, test_group_accessible_by_regular
):
    """Test that DELETE /api/groups/{id} fails to delete a group by regular user
    with valid id"""
    group_id = test_group_accessible_by_regular.id

    # attempt to delete the group
    response = await client.delete(f"/api/groups/{group_id}", headers=user_auth_headers)
    assert response.status_code == 403  # Forbidden

    # Verify the group still exists by retrieving it
    get_response = await client.get(
        f"/api/groups/{group_id}", headers=user_auth_headers
    )
    assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_delete_group_admin_invalid_id(client: AsyncClient, auth_headers):
    """Test that DELETE /api/groups/{id} fails to delete a group by admin
    with invalid id"""
    response = await client.delete("/api/groups/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_group_regular_user_invalid_id(
    client: AsyncClient, user_auth_headers
):
    """Test that DELETE /api/groups/{id} fails to delete a group by regular user
    with invalid id"""
    response = await client.delete("/api/groups/99999", headers=user_auth_headers)
    assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_delete_group_admin_string_id(client: AsyncClient, auth_headers):
    """Test that DELETE /api/groups/{id} fails to
    delete a group by admin with string id"""
    response = await client.delete("/api/groups/invalid_id", headers=auth_headers)
    assert response.status_code == 422
