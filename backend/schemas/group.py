"""
Group Pydantic schemas for request/response validation
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class GroupMemberRole(str, Enum):
    """Valid roles for group members"""

    MEMBER = "member"
    MODERATOR = "moderator"
    OWNER = "owner"


class GroupBase(BaseModel):
    """Base schema with common group fields"""

    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    """Schema for creating a new group"""

    pass


class GroupUpdate(BaseModel):
    """Schema for updating a group"""

    name: Optional[str] = None
    description: Optional[str] = None


class UserInGroup(BaseModel):
    """User information included in group membership"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    joined_at: datetime


class GroupMember(BaseModel):
    """Group membership information"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    email: str
    role: str  # 'member', 'moderator', or 'owner' (group membership role)
    group_role: str  # Alias for role (for backward compatibility)
    user_role: Optional[str] = None  # User's system role ('admin', 'user', 'manager')
    joined_at: datetime
    avatar_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    child_dob: Optional[date] = None
    updated_at: Optional[datetime] = None  # Last active date

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate that role is one of the allowed values"""
        allowed_roles = ["member", "moderator", "owner"]
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v


class GroupResponse(GroupBase):
    """Group response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    member_count: Optional[int] = None  # Number of members


class GroupDetailResponse(GroupResponse):
    """Detailed group response with members"""

    model_config = ConfigDict(from_attributes=True)

    members: List[GroupMember] = []


class InviteBase(BaseModel):
    """Base schema for invites"""

    email: EmailStr
    group_id: int


class InviteCreate(InviteBase):
    """Schema for creating an invite"""

    pass


class InviteResponse(BaseModel):
    """Invite response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    group_id: int
    group_name: Optional[str] = None
    invited_by: int
    inviter_username: Optional[str] = None
    expires_at: datetime
    used_at: Optional[datetime] = None
    created_at: datetime


class InviteAccept(BaseModel):
    """Schema for accepting an invite"""

    token: str
