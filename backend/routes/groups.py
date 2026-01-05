"""
Group API endpoints
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from auth import get_current_active_user, require_group_manager, security_scheme
from database import get_db
from models import (
    Course,
    CourseGroup,
    Group,
    User,
    UserGroup,
)
from schemas.course import CourseResponse
from schemas.group import (
    GroupCreate,
    GroupDetailResponse,
    GroupMember,
    GroupResponse,
    GroupUpdate,
)

router = APIRouter(prefix="/groups", tags=["groups"])


def can_manage_group(user: User) -> bool:
    """
    Check if a user can manage groups.
    Managers and admins can manage groups.
    """
    if user.role is None:
        return False
    return user.role.name in ["admin", "manager"]


async def get_group_or_404(
    group_id: int, db: AsyncSession, current_user: User
) -> Group:
    """
    Get a group by ID or raise 404.
    Also checks if user has access (must be manager/admin or member).
    """
    result = await db.execute(
        select(Group).where(Group.id == group_id).options(joinedload(Group.creator))
    )
    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found",
        )

    # Check if user can access this group
    # Admins and managers can access any group
    if can_manage_group(current_user):
        return group

    # Regular users can only access groups they're members of
    membership_result = await db.execute(
        select(UserGroup).where(
            UserGroup.user_id == current_user.id, UserGroup.group_id == group_id
        )
    )
    membership = membership_result.scalar_one_or_none()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this group",
        )

    return group


@router.get(
    "",
    response_model=List[GroupResponse],
    dependencies=[Security(security_scheme)],
)
async def get_all_groups(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all groups accessible to the current user.
    - Admins and managers see all groups
    - Regular users see only groups they're members of
    """
    if can_manage_group(current_user):
        # Managers and admins see all groups
        result = await db.execute(
            select(Group).options(joinedload(Group.creator)).order_by(Group.created_at)
        )
        groups = result.unique().scalars().all()
    else:
        # Regular users see only their groups
        result = await db.execute(
            select(Group)
            .join(UserGroup, Group.id == UserGroup.group_id)
            .where(UserGroup.user_id == current_user.id)
            .options(joinedload(Group.creator))
            .order_by(Group.created_at)
        )
        groups = result.unique().scalars().all()

    # Add member count to each group
    group_list = []
    for group in groups:
        member_count_result = await db.execute(
            select(UserGroup).where(UserGroup.group_id == group.id)
        )
        member_count = len(member_count_result.scalars().all())
        group_dict = {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_by": group.created_by,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
            "member_count": member_count,
        }
        group_list.append(group_dict)

    return group_list


@router.get(
    "/{group_id}",
    response_model=GroupDetailResponse,
    dependencies=[Security(security_scheme)],
)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single group by ID with its members.
    """
    group = await get_group_or_404(group_id, db, current_user)

    # Get all members with user and role relationships loaded
    members_result = await db.execute(
        select(UserGroup)
        .where(UserGroup.group_id == group_id)
        .options(joinedload(UserGroup.user).joinedload(User.role))
        .order_by(UserGroup.joined_at)
    )
    memberships = members_result.unique().scalars().all()

    # Format members
    members = []
    for membership in memberships:
        # Get user's system role name
        user_role_name = membership.user.role.name if membership.user.role else None

        members.append(
            GroupMember(
                user_id=membership.user.id,
                username=membership.user.username,
                email=membership.user.email,
                role=membership.role,
                group_role=membership.role,  # Group membership role
                user_role=user_role_name,  # User's system role
                joined_at=membership.joined_at,
                avatar_url=membership.user.avatar_url,
                first_name=membership.user.first_name,
                last_name=membership.user.last_name,
                child_dob=membership.user.child_dob,
                updated_at=membership.user.updated_at,
            )
        )

    # Get member count
    member_count_result = await db.execute(
        select(UserGroup).where(UserGroup.group_id == group_id)
    )
    member_count = len(member_count_result.scalars().all())

    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_by": group.created_by,
        "created_at": group.created_at,
        "updated_at": group.updated_at,
        "member_count": member_count,
        "members": members,
    }


@router.get(
    "/{group_id}/courses",
    response_model=List[CourseResponse],
    dependencies=[Security(security_scheme)],
)
async def get_group_courses(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all courses assigned to a specific group.
    User must have access to the group (admin, manager, or member).
    """
    # Verify user has access to the group
    await get_group_or_404(group_id, db, current_user)

    # Get courses assigned to this group
    result = await db.execute(
        select(Course)
        .join(CourseGroup, Course.id == CourseGroup.course_id)
        .where(CourseGroup.group_id == group_id)
        .order_by(CourseGroup.ordering, Course.created_at)
    )
    courses = result.scalars().all()

    # Format response
    course_list = []
    for course in courses:
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "module_count": 0,  # Modules will be implemented by students
        }
        course_list.append(course_dict)

    return course_list


@router.post(
    "",
    response_model=GroupResponse,
    status_code=201,
    dependencies=[Security(security_scheme)],
)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(require_group_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new group.
    Requires manager or admin role.
    """
    # Validate name is not empty
    name = group_data.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name cannot be empty",
        )

    # Check if group name already exists (optional - you might want to allow duplicates)
    # For now, we'll allow duplicate names

    # Create the group
    db_group = Group(
        name=name,
        description=group_data.description.strip() if group_data.description else None,
        created_by=current_user.id,
    )

    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)

    # Automatically add creator as owner
    membership = UserGroup(user_id=current_user.id, group_id=db_group.id, role="owner")
    db.add(membership)
    await db.commit()

    # Reload with creator relationship
    result = await db.execute(
        select(Group).where(Group.id == db_group.id).options(joinedload(Group.creator))
    )
    db_group = result.scalar_one()

    # Get member count (should be 1 for new group - the creator)
    return {
        "id": db_group.id,
        "name": db_group.name,
        "description": db_group.description,
        "created_by": db_group.created_by,
        "created_at": db_group.created_at,
        "updated_at": db_group.updated_at,
        "member_count": 1,
    }


@router.patch(
    "/{group_id}",
    response_model=GroupResponse,
    dependencies=[Security(security_scheme)],
)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    current_user: User = Depends(require_group_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a group.
    Requires manager or admin role.
    """
    group = await get_group_or_404(group_id, db, current_user)

    # Only managers/admins can update (already checked by require_group_manager)
    # Update fields if provided
    if group_data.name is not None:
        name = group_data.name.strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group name cannot be empty",
            )
        group.name = name

    if group_data.description is not None:
        group.description = (
            group_data.description.strip() if group_data.description else None
        )

    group.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(group)

    # Get member count
    member_count_result = await db.execute(
        select(UserGroup).where(UserGroup.group_id == group_id)
    )
    member_count = len(member_count_result.scalars().all())

    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_by": group.created_by,
        "created_at": group.created_at,
        "updated_at": group.updated_at,
        "member_count": member_count,
    }


@router.delete(
    "/{group_id}",
    status_code=204,
    dependencies=[Security(security_scheme)],
)
async def delete_group(
    group_id: int,
    current_user: User = Depends(require_group_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a group.
    Requires manager or admin role.
    """
    group = await get_group_or_404(group_id, db, current_user)

    # Only managers/admins can delete (already checked by require_group_manager)
    await db.delete(group)
    await db.commit()

    return None


@router.post(
    "/{group_id}/members/{user_id}",
    status_code=201,
    dependencies=[Security(security_scheme)],
)
async def add_member_to_group(
    group_id: int,
    user_id: int,
    role: str = Body(default="member", embed=True),
    current_user: User = Depends(require_group_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Add an existing user to a group.
    Requires manager or admin role.

    Optional body parameter: role (default: "member")
    Valid roles: "member", "moderator", "owner"
    """
    # Validate role
    valid_roles = ["member", "moderator", "owner"]
    role = role.lower().strip()
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    # Verify group exists and user can manage it
    group = await get_group_or_404(group_id, db, current_user)

    # Get the user to add
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Check if user is already a member
    existing_membership = await db.execute(
        select(UserGroup).where(
            UserGroup.user_id == user_id, UserGroup.group_id == group_id
        )
    )
    if existing_membership.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this group",
        )

    # Add user to group with specified role
    membership = UserGroup(user_id=user_id, group_id=group_id, role=role)
    db.add(membership)
    await db.commit()

    return {
        "message": f"User {user.username} added to group {group.name} as {role}",
        "role": role,
    }


@router.delete(
    "/{group_id}/members/{user_id}",
    status_code=204,
    dependencies=[Security(security_scheme)],
)
async def remove_member_from_group(
    group_id: int,
    user_id: int,
    current_user: User = Depends(require_group_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a user from a group.
    Requires manager or admin role.
    """
    # Verify group exists and user can manage it
    group = await get_group_or_404(group_id, db, current_user)  # noqa: F841

    # Find the membership
    membership_result = await db.execute(
        select(UserGroup).where(
            UserGroup.user_id == user_id, UserGroup.group_id == group_id
        )
    )
    membership = membership_result.scalar_one_or_none()  # noqa: F841

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this group",
        )

    # Prevent removing the last owner
    if membership.role == "owner":
        # Check if there are other owners
        other_owners_result = await db.execute(
            select(UserGroup).where(
                UserGroup.group_id == group_id,
                UserGroup.role == "owner",
                UserGroup.user_id != user_id,
            )
        )
        if not other_owners_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last owner from the group",
            )

    # Remove membership
    await db.delete(membership)
    await db.commit()

    return None


@router.patch(
    "/{group_id}/members/{user_id}/role",
    status_code=200,
    dependencies=[Security(security_scheme)],
)
async def update_member_role(
    group_id: int,
    user_id: int,
    role: str = Body(embed=True),
    current_user: User = Depends(require_group_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a member's role in a group.
    Requires manager or admin role.

    Body parameter: role (required)
    Valid roles: "member", "moderator", "owner"
    """
    # Validate role
    valid_roles = ["member", "moderator", "owner"]
    role = role.lower().strip()
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    # Verify group exists and user can manage it
    group = await get_group_or_404(group_id, db, current_user)  # noqa: F841

    # Find the membership
    membership_result = await db.execute(
        select(UserGroup).where(
            UserGroup.user_id == user_id, UserGroup.group_id == group_id
        )
    )
    membership = membership_result.scalar_one_or_none()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this group",
        )

    # If changing from owner, ensure there's at least one other owner
    if membership.role == "owner" and role != "owner":
        other_owners_result = await db.execute(
            select(UserGroup).where(
                UserGroup.group_id == group_id,
                UserGroup.role == "owner",
                UserGroup.user_id != user_id,
            )
        )
        if not other_owners_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change role of the last owner. Promote another member to owner first.",  # noqa: E501
            )

    # Update role
    membership.role = role
    await db.commit()
    await db.refresh(membership)

    return {
        "message": f"Member role updated to {role}",
        "user_id": user_id,
        "role": role,
    }


# Progress tracking endpoint removed - will be implemented by students
