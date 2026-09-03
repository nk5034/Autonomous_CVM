"""Add campaign artifact and approval tables.

Revision ID: 20260901_000001
Revises:
Create Date: 2026-09-01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260901_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaign_artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column(
            "artifact_type",
            sa.Enum(
                "SELECTION_BRIEFING",
                "AUDIENCE_DEFINITION",
                "CAMPAIGN_CONFIGURATION",
                "PROPOSITION_SHEET",
                "TREATMENT_SHEET",
                "CONTACT_RULES",
                "VOLUME_CONSTRAINTS",
                "CONTROL_GROUP_DEFINITION",
                "REPORTING_CONFIGURATION",
                name="campaignartifacttype",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "PENDING_APPROVAL",
                "APPROVED",
                "REJECTED",
                "ROLLED_BACK",
                name="campaignartifactstatus",
            ),
            nullable=False,
        ),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("approver", sa.String(length=255), nullable=True),
        sa.Column("approval_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_campaign_artifacts_campaign_id", "campaign_artifacts", ["campaign_id"])

    op.create_table(
        "campaign_artifact_approvals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("artifact_id", sa.Integer(), nullable=False),
        sa.Column("reviewer", sa.String(length=255), nullable=False),
        sa.Column("approved", sa.Boolean(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["artifact_id"], ["campaign_artifacts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_campaign_artifact_approvals_artifact_id",
        "campaign_artifact_approvals",
        ["artifact_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_campaign_artifact_approvals_artifact_id", table_name="campaign_artifact_approvals")
    op.drop_table("campaign_artifact_approvals")

    op.drop_index("ix_campaign_artifacts_campaign_id", table_name="campaign_artifacts")
    op.drop_table("campaign_artifacts")

    sa.Enum(name="campaignartifactstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="campaignartifacttype").drop(op.get_bind(), checkfirst=True)
