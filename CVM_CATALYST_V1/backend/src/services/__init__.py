"""Service package exports.

Imports are intentionally lazy so metadata-only paths do not eagerly import
SQLAlchemy-backed domain services at package import time.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "CampaignDomainService",
    "ApprovalDomainService",
    "DeploymentDomainService",
    "WorkflowDomainService",
    "ExperimentationDomainService",
    "AccessControlDomainService",
    "EnterpriseMetadataService",
    "CampaignArtifactService",
    "CampaignArtifactDbService",
    "SyntheticDataService",
    "CampaignSimulationService",
    "ABTestingService",
]


def __getattr__(name: str) -> Any:
    if name == "EnterpriseMetadataService":
        return getattr(import_module("src.services.metadata_layer"), name)

    if name == "CampaignArtifactService":
        return getattr(import_module("src.services.artifact_generation"), name)

    if name == "CampaignArtifactDbService":
        return getattr(import_module("src.services.artifact_generation_db"), name)

    if name == "SyntheticDataService":
        return getattr(import_module("src.services.synthetic_data"), name)

    if name == "CampaignSimulationService":
        return getattr(import_module("src.services.campaign_simulation"), name)

    if name == "ABTestingService":
        return getattr(import_module("src.services.ab_testing"), name)

    if name in {
        "CampaignDomainService",
        "ApprovalDomainService",
        "DeploymentDomainService",
        "WorkflowDomainService",
        "ExperimentationDomainService",
        "AccessControlDomainService",
    }:
        return getattr(import_module("src.services.domain_services"), name)

    raise AttributeError(f"module 'src.services' has no attribute {name!r}")
