"""RBAC and authorization audit helpers for API endpoints."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from fastapi import Header, HTTPException, Request

from src.core.config.settings import settings
from src.db.database import AsyncSessionLocal
from src.models.entities import AuditLog

logger = logging.getLogger("cvm_catalyst")


class RoleName(str, Enum):
    BUSINESS_USER = "Business User"
    CAMPAIGN_MANAGER = "Campaign Manager"
    APPROVER = "Approver"
    ADMINISTRATOR = "Administrator"
    DEVELOPER = "Developer"


ROLE_ALIASES = {
    "business user": RoleName.BUSINESS_USER,
    "business_user": RoleName.BUSINESS_USER,
    "campaign manager": RoleName.CAMPAIGN_MANAGER,
    "campaign_manager": RoleName.CAMPAIGN_MANAGER,
    "approver": RoleName.APPROVER,
    "administrator": RoleName.ADMINISTRATOR,
    "admin": RoleName.ADMINISTRATOR,
    "developer": RoleName.DEVELOPER,
}


PERMISSIONS_BY_ROLE: dict[RoleName, set[str]] = {
    RoleName.BUSINESS_USER: {
        "metadata.read",
        "synthetic_data.read",
        "campaign.simulation.read",
        "ab_testing.read",
        "campaign.artifacts.read",
        "workflow.read",
    },
    RoleName.CAMPAIGN_MANAGER: {
        "metadata.read",
        "synthetic_data.read",
        "synthetic_data.generate",
        "campaign.simulation.read",
        "campaign.simulation.run",
        "ab_testing.read",
        "ab_testing.run",
        "campaign.artifacts.read",
        "campaign.artifacts.write",
        "campaign.artifacts.export",
        "workflow.read",
        "workflow.run",
    },
    RoleName.APPROVER: {
        "metadata.read",
        "campaign.artifacts.read",
        "campaign.artifacts.approve",
        "workflow.read",
        "workflow.approve",
    },
    RoleName.ADMINISTRATOR: {"*"},
    RoleName.DEVELOPER: {"*"},
}


@dataclass(slots=True)
class CurrentPrincipal:
    user_id: int | None
    email: str | None
    role: RoleName
    permissions: set[str]


def _normalize_role(value: str | None) -> RoleName:
    if value is None or not value.strip():
        return _normalize_role(settings.RBAC_DEFAULT_ROLE)

    normalized = value.strip().lower().replace("-", "_")
    role = ROLE_ALIASES.get(normalized)
    if role is None:
        allowed = ", ".join(role_name.value for role_name in RoleName)
        raise HTTPException(status_code=400, detail=f"Invalid role '{value}'. Allowed roles: {allowed}.")
    return role


def _parse_user_id(value: str | None) -> int | None:
    if value is None or not value.strip():
        return None

    try:
        return int(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="X-User-Id must be an integer.") from exc


def _has_permission(granted_permissions: set[str], required_permission: str) -> bool:
    return "*" in granted_permissions or required_permission in granted_permissions


async def _persist_audit_event(*, principal: CurrentPrincipal, request: Request, required: list[str], allowed: bool) -> None:
    event = AuditLog(
        actor_user_id=principal.user_id,
        aggregate_name="RBAC",
        aggregate_id=f"{request.method}:{request.url.path}",
        event_type="access.granted" if allowed else "access.denied",
        payload={
            "role": principal.role.value,
            "email": principal.email,
            "required_permissions": required,
            "granted_permissions": sorted(principal.permissions),
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        },
    )

    try:
        async with AsyncSessionLocal() as session:
            session.add(event)
            await session.commit()
    except Exception:  # pragma: no cover - authorization must not fail if audit persistence fails.
        logger.warning(
            "Unable to persist RBAC audit event",
            exc_info=True,
            extra={
                "event_type": event.event_type,
                "path": request.url.path,
                "role": principal.role.value,
            },
        )


def require_permissions(required_permissions: Iterable[str]):
    """Create a FastAPI dependency that enforces one-or-many permissions."""
    required = list(required_permissions)

    async def dependency(
        request: Request,
        x_user_role: str | None = Header(default=None, alias="X-User-Role"),
        x_user_id: str | None = Header(default=None, alias="X-User-Id"),
        x_user_email: str | None = Header(default=None, alias="X-User-Email"),
    ) -> CurrentPrincipal:
        role = _normalize_role(x_user_role)
        granted_permissions = PERMISSIONS_BY_ROLE[role]
        principal = CurrentPrincipal(
            user_id=_parse_user_id(x_user_id),
            email=x_user_email,
            role=role,
            permissions=granted_permissions,
        )

        is_allowed = all(_has_permission(granted_permissions, permission) for permission in required)
        await _persist_audit_event(principal=principal, request=request, required=required, allowed=is_allowed)

        if not settings.RBAC_ENABLED:
            request.state.principal = principal
            return principal

        if not is_allowed:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Insufficient permissions. "
                    f"Required: {', '.join(required)}. Role '{role.value}' is not authorized."
                ),
            )

        request.state.principal = principal
        return principal

    return dependency
