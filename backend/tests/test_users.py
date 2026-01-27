"""
Contract-level tests for the /api/users endpoint
"""

import pytest
from httpx import AsyncClient


# -------------------
# Test GET /api/users
# -------------------
@pytest.mark.asyncio
async def test_get_all_users_requires_auth(client: AsyncClient):
    """Test that GET /api/users requires authentication"""
    response = await client.get("/api/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_users_with_auth(client: AsyncClient, auth_headers, admin_user):
    """Test that GET /api/users returns list of users when authenticated"""
    response = await client.get("/api/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Verify the list contains at least the admin user we created
    assert len(data) >= 1
    # Verify each item in the list has the expected user structure
    for user in data:
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "role" in user
        assert "password" not in user  # Password should never be in response

    # Verify the admin user is in the list
    admin_usernames = [user["username"] for user in data]
    assert "admin" in admin_usernames


# End ----------------


# ------------------------
# Test GET /api/users/{id}
# ------------------------
@pytest.mark.asyncio
async def test_get_user_by_id_requires_auth(client: AsyncClient):
    """Test that GET /api/users/{id} requires authentication"""
    response = await client.get("/api/users/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(client: AsyncClient, auth_headers):
    """Test that GET /api/users/{id} returns 404 for non-existent user"""
    response = await client.get("/api/users/99999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_user_by_id_incorrect_type_fields(client: AsyncClient, auth_headers):
    """Test that GET /api/users/{id} returns 422 for non-int required id input"""
    response = await client.get("/api/users/eleven", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user_by_id_success(client: AsyncClient, auth_headers):
    """Test that GET /api/users/{id} returns 200 if a user matching the
    id is found, has all expected fields, and doesn't return the user's password"""
    response = await client.get("/api/users/1", headers=auth_headers)
    assert response.status_code == 200
    user = response.json()

    #  {id: int, role: RoleInUser, email_verified: bool, is_active: bool,
    # created_at: datetime, updated_at: datetime}
    assert "id" in user
    assert "role" in user
    assert "email_verified" in user
    assert "is_active" in user
    assert "created_at" in user
    assert "updated_at" in user

    assert "password" not in user


# End ---------------


# --------------------
# Test POST /api/users
# --------------------
@pytest.mark.asyncio
async def test_create_user_requires_auth(client: AsyncClient):
    """Test that POST /api/users requires authentication"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    response = await client.post("/api/users", json=user_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient, auth_headers, test_db):
    """Test that POST /api/users creates a user successfully"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data  # Password should not be in response

    # Verify the user was actually created by retrieving it through the API
    user_id = data["id"]
    get_response = await client.get(f"/api/users/{user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_user = get_response.json()
    assert retrieved_user["username"] == "newuser"
    assert retrieved_user["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_create_user_missing_fields(client: AsyncClient, auth_headers):
    """Test that POST /api/users returns 422 for missing required fields"""
    user_data = {
        "username": "testuser"
        # Missing email and password
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_duplicate_username(
    client: AsyncClient, auth_headers, test_db
):
    """Test that POST /api/users returns error for duplicate username"""
    user_data = {
        "username": "duplicate",
        "email": "first@example.com",
        "password": "password123",
        "role": "user",
    }
    # Create first user
    create_response = await client.post(
        "/api/users", json=user_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    first_user_id = create_response.json()["id"]

    # Verify the first user was actually created
    get_response = await client.get(f"/api/users/{first_user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["username"] == "duplicate"

    # Try to create duplicate username (different email)
    user_data["email"] = "second@example.com"
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

    # Verify the first user still exists and wasn't affected
    get_response = await client.get(f"/api/users/{first_user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert (
        get_response.json()["email"] == "first@example.com"
    )  # Original email unchanged


# End ------------------------


# --------------------------
# Test PATCh /api/users/{id}
# --------------------------
@pytest.mark.asyncio
async def test_patch_user_by_id_requires_auth(client: AsyncClient):
    """Test that PATCH /api/users/{id} requires authentication"""
    profile_data = {
        "first_name": "updatedFirstName",
    }
    response = await client.patch("/api/users/1", json=profile_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patch_user_by_id_not_found(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 404 for non-existent user"""
    profile_data = {
        "first_name": "updatedFirstName",
    }
    response = await client.patch(
        "/api/users/999999", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_user_by_id_not_int(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 422 for invalid id"""
    profile_data = {
        "first_name": "updatedFirstName",
    }
    response = await client.patch(
        "/api/users/eleven", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_by_id_empty_params_success(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} succeeds when given empty parameters,
    because all params are optional"""
    profile_data = {}
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_patch_user_by_id_no_params_given(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 422 because no paremeters were given"""
    response = await client.patch("/api/users/1", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_by_id_bad_params_given(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 422 for invalid parameter types"""
    # Most params are strings. They are not automatically converted to string.
    profile_data = {"first_name": 391}
    # NOTE: It is interesting that this one won't go through, but other
    # type conversions (checked in PATCH /api/users/{id}/status) go through just fine
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 422

    # Give a bad/un-convertable date value, which should cause 422 error
    profile_data = {"child_dob": "BAD DATE THERES NO WAY THIS CONVERTS"}
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_by_id_all_fields_success(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 200 for successful
    update of all fields and that the update persists"""
    # Get previous data for user to store for comparisson
    response = await client.get("/api/users/1", headers=auth_headers)
    original_user_data = response.json()

    profile_data = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        "child_name": "UpdatedChildName",
        "child_sex_assigned_at_birth": "UpdatedChildSexAssignedAtBirth",
        "child_dob": "2026-01-29",
        "avatar_url": "UpdatedURL",
    }
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 200  # Check the error code
    # Then re-retrieve the data to validated it persisted in the DB
    response = await client.get("/api/users/1", headers=auth_headers)
    updated_user_data = response.json()

    # Compare each value
    assert (
        original_user_data["first_name"] != updated_user_data["first_name"]
        and updated_user_data["first_name"] == profile_data["first_name"]
    )
    assert (
        original_user_data["last_name"] != updated_user_data["last_name"]
        and updated_user_data["last_name"] == profile_data["last_name"]
    )
    assert (
        original_user_data["child_name"] != updated_user_data["child_name"]
        and updated_user_data["child_name"] == profile_data["child_name"]
    )
    assert (
        original_user_data["child_sex_assigned_at_birth"]
        != updated_user_data["child_sex_assigned_at_birth"]
        and updated_user_data["child_sex_assigned_at_birth"]
        == profile_data["child_sex_assigned_at_birth"]
    )
    assert (
        original_user_data["child_dob"] != updated_user_data["child_dob"]
        and updated_user_data["child_dob"] == profile_data["child_dob"]
    )
    assert (
        original_user_data["avatar_url"] != updated_user_data["avatar_url"]
        and updated_user_data["avatar_url"] == profile_data["avatar_url"]
    )


@pytest.mark.asyncio
async def test_patch_user_by_id_partial_fields_success(
    client: AsyncClient, auth_headers
):
    """Test that PATCH /api/users/{id} returns 200 for successful update
    which changes some of the fields and that the update persists"""
    # Get previous data for user to store for comparisson
    response = await client.get("/api/users/1", headers=auth_headers)
    original_user_data = response.json()

    profile_data = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        # Only update some of the fields
        "CHILDNAME": "Shouldn't be seen",
    }
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 200  # Check the error code
    # Then re-retrieve the data to validated it persisted in the DB
    response = await client.get("/api/users/1", headers=auth_headers)
    updated_user_data = response.json()

    # First and last name should be updated, and should be different
    # from the original values
    assert (
        original_user_data["first_name"] != updated_user_data["first_name"]
        and updated_user_data["first_name"] == profile_data["first_name"]
    )
    assert (
        original_user_data["last_name"] != updated_user_data["last_name"]
        and updated_user_data["last_name"] == profile_data["last_name"]
    )

    # The rest should not have been updated
    assert original_user_data["child_name"] == updated_user_data["child_name"]
    assert (
        original_user_data["child_sex_assigned_at_birth"]
        == updated_user_data["child_sex_assigned_at_birth"]
    )
    assert original_user_data["child_dob"] == updated_user_data["child_dob"]
    assert original_user_data["avatar_url"] == updated_user_data["avatar_url"]

    assert "CHILDNAME" not in updated_user_data


# End ------------------------


# --------------------------
# Test DELETE /api/users/{id}
# --------------------------
@pytest.mark.asyncio
async def test_delete_user_by_id_requires_auth(client: AsyncClient):
    """Test that DELETE /api/users/{id} requires authentication"""
    response = await client.delete(
        "/api/users/1",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_by_id_not_found(client: AsyncClient, auth_headers):
    """Test that DELETE /api/users/{id} returns 404 for non-existent user"""
    response = await client.delete("/api/users/99999999999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_by_id_incorrect_type_fields(
    client: AsyncClient, auth_headers
):
    """Test that DELETE /api/users/{id} returns 422 because
    invalid paremeters were given"""
    response = await client.delete("/api/users/eleven", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_user_by_id_prevent_delete_self(
    client: AsyncClient, auth_headers, admin_user
):
    """Test that DELETE /api/users/{id} returns 400 if you try to delete yourself"""

    response = await client.delete(f"/api/users/{admin_user.id}", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_user_by_id_successful(client: AsyncClient, auth_headers):
    """Test that DELETE /api/users/{id} returns 204 when a user is
    deleted and that it persists"""
    # Add a second user to the DB to test deleting it
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data

    id_to_delete = data["id"]
    # Confirm that the new user exists before deletion
    response = await client.get(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 200

    # I checked above, the admin user is id = 1, so  I can't
    # delete that one. Deleting new user instead
    response = await client.delete(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 204  # Verify the deletion code

    with pytest.raises(
        ValueError
    ):  # Checks if trying to get the json of the response would
        response.json()  # raise an error, which it should
    # Then verify that it's actually gone
    response = await client.get(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 404


# End ------------------------


# ---------------------------------
# Test PATCH /api/users/{id}/status
# ---------------------------------
# NOTE: Many of the initial tests which test for 404 or 422 failures
#   use a random int for user_id, because they should fail before
#   getting to use it, therefore it is okay that I have not validated
#   that it's a valid id. I do validate this for tests where it matters
# NOTE 2: I am pretty sure the test DB that's set up ONLY has the admin
#    user initially. For most tests, I need to first insert a second
#   user so that the url is valid (I can't use 1, because the admin
#   can't update itself, and I need to use a valid ID to test other
#   aspects of the DB)
@pytest.mark.asyncio
async def test_patch_user_status_by_id_requires_auth(client: AsyncClient):
    """Test that PATCH /api/users/{id}/status requires authentication"""
    status_data = {"user_id": 55, "is_active": False}
    response = await client.patch("/api/users/1/status", json=status_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patch_user_status_by_id_not_found(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/status returns 404 for non-existent user"""
    status_data = {"user_id": 55, "is_active": False}
    response = await client.patch(
        "/api/users/999999/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_user_status_by_id_not_int(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/status returns 422 for invalid id in the URL"""
    status_data = {"user_id": 55, "is_active": False}
    response = await client.patch(
        "/api/users/eleven/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_status_by_id_no_parameters(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/status returns 422 because
    no paremeters were given"""

    # From here on, I have to insert a new user to use their ID for
    # the url
    # Add a second user to the DB to test with a correct URL
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    data = response.json()
    assert "id" in data
    id_to_use = data["id"]

    # Actual test
    response = await client.patch(
        f"/api/users/{id_to_use}/status", headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_status_by_id_bad_parameters(
    client: AsyncClient, auth_headers
):
    """Test that PATCH /api/users/{id}/status returns 422 for invalid
    parameter types and empty parameters"""
    # Add a second user to the DB to test with a correct URL
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    data = response.json()
    assert "id" in data
    id_to_use = data["id"]

    # Actual tests
    # Empty params
    status_data = {}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422

    # Bad type for user_id
    status_data = {"user_id": "eleven", "is_active": False}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422

    # Bad type for is_active
    status_data = {"user_id": 55, "is_active": "dkgbdsflkjb"}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_status_by_id_convertable_parameters(
    client: AsyncClient, auth_headers
):
    """Test that PATCH /api/users/{id}/status returns 200 for parameters
    where the types can be converted"""
    # Add a second user to the DB to test with a correct URL
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    data = response.json()
    assert "id" in data
    id_to_use = data["id"]

    # Actual tests
    # Permissible type for user_id
    status_data = {"user_id": "2", "is_active": False}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 200

    # Permissible type for is_active
    status_data = {"user_id": 55, "is_active": "false"}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 200
    # NOTE: Interestingly, these bad parameters can convert, wherease the
    # first_name parameter of PATCH /api/users/{id} can't convert from int to string


@pytest.mark.asyncio
async def test_patch_user_status_by_id_prevent_disable_self(
    client: AsyncClient, auth_headers, admin_user
):
    """Test that PATCH /api/users/{id}/status returns 400 if you try
    to disable yourself"""
    status_data = {"user_id": admin_user.id, "is_active": False}
    response = await client.patch(
        f"/api/users/{admin_user.id}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_patch_user_status_by_id_successful(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/status returns 200 for successful
    status update and that the update persists"""
    # Add a second user to the DB to test with a correct URL
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    original_data = response.json()
    assert "id" in original_data
    id_to_use = original_data["id"]

    # Actual test
    status_data = {
        "user_id": id_to_use,
        "is_active": not original_data[
            "is_active"
        ],  # Negate the original activity status
    }
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 200  # Confirm the code
    response_data = response.json()

    # Check that the user is returned
    assert (
        "id" in response_data
        and "role" in response_data
        and "email_verified" in response_data
        and "is_active" in response_data
        and "created_at" in response_data
        and "updated_at" in response_data
    )

    # Then check the user's updated info persisted
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    updated_data = response.json()

    assert (
        original_data["is_active"] != updated_data["is_active"]
    )  # Check that they're opposites


# End ----------------------


# ---------------------------------
# Test PATCH /api/users/{id}/role
# ---------------------------------
# NOTE: Many of the initial tests which test for 404 or 422 failures
#   use a random int for user_id, because they should fail before
#   getting to use it, therefore it is okay that I have not validated
#   that it's a valid id. I do validate this for tests where it matters
# NOTE 2: I am pretty sure the test DB that's set up ONLY has the admin
#   user initially. For most tests, I need to first insert a second
#   user so that the url is valid (I can't use 1, because the admin
#   can't update itself, and I need to use a valid ID to test other
#   aspects of the DB)
@pytest.mark.asyncio
async def test_patch_user_role_by_id_requires_auth(client: AsyncClient):
    """Test that PATCH /api/users/{id}/role requires authentication"""
    role_data = {"user_id": 55, "role": "manager"}
    response = await client.patch("/api/users/1/role", json=role_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patch_user_role_by_id_not_found(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/role returns 404 for non-existent user"""
    role_data = {"user_id": 55, "role": "manager"}
    response = await client.patch(
        "/api/users/999999/role", json=role_data, headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_user_role_by_id_not_int(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/role returns 422 for invalid
    id in the URL"""
    role_data = {"user_id": 55, "role": "manager"}
    response = await client.patch(
        "/api/users/eleven/role", json=role_data, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_role_by_id_no_parameters(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/role returns 422 because no
    paremeters were given"""

    # From here on, I have to insert a new user to use their ID for the url
    # Add a second user to the DB to test with a correct URL
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    data = response.json()
    assert "id" in data
    id_to_use = data["id"]

    # Actual test
    response = await client.patch(f"/api/users/{id_to_use}/role", headers=auth_headers)


@pytest.mark.asyncio
async def test_patch_user_role_by_id_bad_parameters(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/role returns 422 for invalid
    parameter types and empty parameters"""
    # Add a second user to the DB to test with a correct URL
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    data = response.json()
    assert "id" in data
    id_to_use = data["id"]

    # Actual tests
    # Empty params
    role_data = {}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 422

    # bad type for user_id
    role_data = {"user_id": "eleven", "role": "manager"}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 422

    # bad type for role, as in integer etc
    role_data = {"user_id": id_to_use, "role": 7983298}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_role_by_id_invalid_role(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/role returns 400 for invalid role given"""
    # Add a second user to the DB to test with a correct URL
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    data = response.json()
    assert "id" in data
    id_to_use = data["id"]

    # Actual test
    role_data = {"user_id": id_to_use, "role": "notAdmin"}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_patch_user_role_by_id_convertable_parameters(
    client: AsyncClient, auth_headers
):
    """Test that PATCH /api/users/{id}/role returns 200 for parameters
    where the types can be converted"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    data = response.json()
    assert "id" in data
    id_to_use = data["id"]

    # Actual test
    # Permissible type for user_id
    role_data = {"user_id": "2", "role": "manager"}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_patch_user_role_by_id_prevent_change_own_role(
    client: AsyncClient, auth_headers, admin_user
):
    """Test that PATCH /api/users/{id}/role returns 400 if you
    try to change your role"""
    role_data = {"user_id": admin_user.id, "role": "user"}
    response = await client.patch(
        f"/api/users/{admin_user.id}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_patch_user_role_by_id_successful(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id}/status returns 200 for
    successful status update and that the update persists"""
    # Add a second user to the DB to test with a correct URL
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201  # Make sure it was made
    original_data = response.json()
    assert "id" in original_data
    id_to_use = original_data["id"]

    # Actual test
    role_data = {
        "user_id": id_to_use,
        "role": "manager",  # New role from the original one set
    }
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 200
    response_data = response.json()

    # Check that the user is returned
    assert (
        "id" in response_data
        and "role" in response_data
        and "email_verified" in response_data
        and "is_active" in response_data
        and "created_at" in response_data
        and "updated_at" in response_data
    )

    # Then check that the updated info has persisted
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    updated_data = response.json()

    assert original_data["role"] != updated_data["role"]
