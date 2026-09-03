"""LangGraph definition for campaign orchestration."""
from __future__ import annotations

from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from src.workflows.orchestration.nodes import (
    ab_testing_node,
    audience_design_node,
    briefing_author_node,
    briefing_intake_node,
    briefing_validation_node,
    business_approval_node,
    campaign_configuration_node,
    control_router_node,
    deployment_node,
    reporting_node,
    simulation_node,
    testing_platform_node,
    test_execution_node,
    test_generation_node,
)
from src.workflows.orchestration.state import CampaignState, ORDERED_NODES, WorkflowRunStatus


def build_initial_state(
    campaign_id: int,
    workflow_id: str,
    thread_id: str | None = None,
) -> CampaignState:
    """Build initial campaign state for a new workflow run."""
    return CampaignState(
        campaign_id=campaign_id,
        workflow_id=workflow_id,
        thread_id=thread_id or f"thread-{uuid4().hex[:12]}",
        next_node=ORDERED_NODES[0],
    )


def entry_router(raw_state: dict) -> dict:
    """Pass-through node for centralized entry routing."""
    return raw_state


def route_from_entry(raw_state: dict) -> str:
    state = CampaignState.from_dict(raw_state)
    if state.next_node is None:
        return END
    return state.next_node.value


def route_after_control(raw_state: dict) -> str:
    state = CampaignState.from_dict(raw_state)

    if state.status in {
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.FAILED,
        WorkflowRunStatus.PAUSED,
        WorkflowRunStatus.WAITING_APPROVAL,
    }:
        return END

    if state.next_node is None:
        return END

    return state.next_node.value


def compile_campaign_graph():
    """Compile and return campaign workflow graph."""
    graph = StateGraph(dict)

    graph.add_node("entry_router", entry_router)
    graph.add_node("briefing_intake", briefing_intake_node)
    graph.add_node("briefing_author", briefing_author_node)
    graph.add_node("briefing_validation", briefing_validation_node)
    graph.add_node("audience_design", audience_design_node)
    graph.add_node("campaign_configuration", campaign_configuration_node)
    graph.add_node("test_generation", test_generation_node)
    graph.add_node("test_execution", test_execution_node)
    graph.add_node("testing_platform", testing_platform_node)
    graph.add_node("simulation", simulation_node)
    graph.add_node("ab_testing", ab_testing_node)
    graph.add_node("business_approval", business_approval_node)
    graph.add_node("deployment", deployment_node)
    graph.add_node("reporting", reporting_node)
    graph.add_node("control_router", control_router_node)

    graph.add_edge(START, "entry_router")
    graph.add_conditional_edges(
        "entry_router",
        route_from_entry,
        {
            "briefing_intake": "briefing_intake",
            "briefing_author": "briefing_author",
            "briefing_validation": "briefing_validation",
            "audience_design": "audience_design",
            "campaign_configuration": "campaign_configuration",
            "test_generation": "test_generation",
            "test_execution": "test_execution",
            "testing_platform": "testing_platform",
            "simulation": "simulation",
            "ab_testing": "ab_testing",
            "business_approval": "business_approval",
            "deployment": "deployment",
            "reporting": "reporting",
            END: END,
        },
    )

    for node_name in [
        "briefing_intake",
        "briefing_author",
        "briefing_validation",
        "audience_design",
        "campaign_configuration",
        "test_generation",
        "test_execution",
        "testing_platform",
        "simulation",
        "ab_testing",
        "business_approval",
        "deployment",
        "reporting",
    ]:
        graph.add_edge(node_name, "control_router")

    graph.add_conditional_edges(
        "control_router",
        route_after_control,
        {
            "briefing_intake": "briefing_intake",
            "briefing_author": "briefing_author",
            "briefing_validation": "briefing_validation",
            "audience_design": "audience_design",
            "campaign_configuration": "campaign_configuration",
            "test_generation": "test_generation",
            "test_execution": "test_execution",
            "testing_platform": "testing_platform",
            "simulation": "simulation",
            "ab_testing": "ab_testing",
            "business_approval": "business_approval",
            "deployment": "deployment",
            "reporting": "reporting",
            END: END,
        },
    )

    return graph.compile()
