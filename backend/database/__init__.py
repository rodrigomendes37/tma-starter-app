"""
Database connection and session management
"""

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Get DATABASE_URL from environment variable, fallback to local development
# Format: postgresql+asyncpg://username:password@host:port/database_name
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine - this manages the connection pool
# Think of it as a "factory" that creates database connections
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,  # Increase base pool size
    max_overflow=20,  # Allow more overflow connections
    pool_pre_ping=True,  # Verify connections before using (prevents stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour (prevents database timeouts)
    connect_args={
        "server_settings": {
            "application_name": "todo_api",  # Helps with database monitoring
        }
    },
)

# Create a session factory - this creates individual database sessions
# Each request will get its own session to query the database
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """
    Generator function that yields a database session.

    The 'yield' keyword is special - it:
    1. Creates a session when the function is called
    2. Gives it to your endpoint function
    3. Closes the session when the endpoint finishes

    This ensures database connections are properly cleaned up.
    """
    async with AsyncSessionLocal() as session:
        yield session  # Give the session to the endpoint
        # After the endpoint finishes, the session is automatically closed
