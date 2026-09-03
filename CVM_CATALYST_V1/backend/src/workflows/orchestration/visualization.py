"""Graph visualization helpers for the campaign LangGraph workflow."""
from __future__ import annotations


def mermaid_workflow_diagram() -> str:
    """Return a Mermaid diagram of the campaign orchestration flow."""
    return """flowchart TD
    S([Start]) --> BI[Briefing Intake]
    BI --> BA[Briefing Author]
    BA --> BV[Briefing Validation]
    BV --> AD[Audience Design]
    AD --> CC[Campaign Configuration]
    CC --> TG[Test Generation]
    TG --> TE[Test Execution]
    TE --> TP[Testing Platform]
    TP --> SM[Simulation]
    SM --> AB[AB Testing]
    AB --> AP[Business Approval]
    AP -->|Approved| DP[Deployment]
    AP -->|Waiting Approval| WA[[Waiting Approval]]
    WA --> RSM[Resume]
    RSM --> AP
    DP --> RP[Reporting]
    RP --> E([End])

    BI -->|Pause| PZ[[Paused]]
    BA -->|Pause| PZ
    BV -->|Pause| PZ
    AD -->|Pause| PZ
    CC -->|Pause| PZ
    TG -->|Pause| PZ
    TE -->|Pause| PZ
    TP -->|Pause| PZ
    SM -->|Pause| PZ
    AB -->|Pause| PZ
    AP -->|Pause| PZ
    DP -->|Pause| PZ
    PZ --> RSM
"""
