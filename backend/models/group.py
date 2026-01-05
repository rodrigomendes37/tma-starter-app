"""
Group model for managing user groups
"""

from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )  # User who created the group (must be manager or admin)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_groups")
    # Many-to-many relationship with users through UserGroup
    members = relationship(
        "UserGroup", back_populates="group", cascade="all, delete-orphan"
    )


class UserGroup(Base):
    """
    Many-to-many relationship between users and groups.
    Represents group membership.
    """

    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    role = Column(
        String(20), nullable=False, default="member", index=True
    )  # 'member', 'moderator', or 'owner'
    joined_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="group_memberships")
    group = relationship("Group", back_populates="members")

    # Ensure a user can only be in a group once
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_user_group"),)
