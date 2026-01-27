"""
Pytest configuration and fixtures for testing
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import get_db
from models import Base, Role, User
from server import app

# Create test database (in-memory SQLite)
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# Override the get_db dependency to use test database
async def override_get_db():
    """Override get_db to use test database"""
    async with TestSessionLocal() as session:
        yield session


# Apply the override
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
async def test_db():
    """Create and drop test database tables for each test"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed required roles
    async with TestSessionLocal() as session:

        # Create all required roles
        roles = [
            Role(name="user", description="Standard user role"),
            Role(name="manager", description="Group manager role"),
            Role(name="admin", description="Administrator role"),
        ]
        for role in roles:
            session.add(role)
        await session.commit()

    yield test_engine

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(test_db):
    """Create test client with test database"""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def admin_user(test_db):
    """Create an admin user for testing (roles already exist from test_db fixture)"""
    async with TestSessionLocal() as session:
        from sqlalchemy.future import select
        from sqlalchemy.orm import joinedload

        # Get admin role (already created by test_db fixture)
        result = await session.execute(select(Role).where(Role.name == "admin"))
        admin_role = result.scalar_one()

        # Create admin user
        admin = User(
            username="admin",
            email="admin@test.com",
            hashed_password="$2b$12$dummy",  # Dummy hash for testing
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        # Load role relationship
        result = await session.execute(
            select(User).where(User.id == admin.id).options(joinedload(User.role))
        )
        admin_with_role = result.scalar_one()

        yield admin_with_role


@pytest.fixture
async def auth_headers(client, admin_user, test_db):
    """Get authentication headers by overriding auth dependencies"""
    from auth import get_current_user, require_admin

    async def override_get_current_user():
        return admin_user

    async def override_require_admin():
        return admin_user

    # Override authentication dependencies to return our test admin user
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[require_admin] = override_require_admin

    yield {"Authorization": "Bearer test-token"}

    # Clean up overrides after test
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)


@pytest.fixture
async def regular_user(test_db):
    """
    Create a regular user (role: "user") for testing

    Use when you need to test endpoints that should work for any authenticated user,
    or when testing that non-admin users are denied access to admin-only endpoints.
    """
    async with TestSessionLocal() as session:
        from sqlalchemy.future import select
        from sqlalchemy.orm import joinedload

        # Get user role
        result = await session.execute(select(Role).where(Role.name == "user"))
        user_role = result.scalar_one()

        # Create regular user
        user = User(
            username="regular_user",
            email="user@test.com",
            hashed_password="$2b$12$dummy",
            role_id=user_role.id,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Load with role relationship
        result = await session.execute(
            select(User).where(User.id == user.id).options(joinedload(User.role))
        )
        user_with_role = result.scalar_one()

        yield user_with_role


@pytest.fixture
async def user_auth_headers(client, regular_user, test_db):
    """
    Get authentication headers for a regular user (non-admin)

    Usage in tests:
        async def test_user_cannot_create_course(client, user_auth_headers):
            response = await client.post(
                "/courses",
                json={"name": "Test Course"},
                headers=user_auth_headers
            )
            assert response.status_code == 403  # Forbidden
    """
    from auth import get_current_active_user, get_current_user

    async def override_get_current_user():
        return regular_user

    async def override_get_current_active_user():
        return regular_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    yield {"Authorization": "Bearer test-token"}

    # Cleanup
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_current_active_user, None)


# fixture for adding a course for testing
@pytest.fixture
async def create_course(admin_user, test_db):
    from datetime import datetime

    from models.course import Course

    async with TestSessionLocal() as session:
        course = Course(
            title="Test Course",
            description="A course for testing",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(course)
        await session.commit()
        await session.refresh(course)
        return course
