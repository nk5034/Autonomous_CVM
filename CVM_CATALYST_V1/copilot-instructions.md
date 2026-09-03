# CVM Catalyst

This project implements an agentic campaign management platform.

## Architecture

- LangGraph is the workflow orchestrator
- CrewAI agents perform specialist tasks
- Pydantic models validate all inputs and outputs
- Humans remain in control of every stage

## Core Principles

- Never change business intent
- Every artifact must be editable by humans
- Every workflow supports human approval
- Every workflow supports manual override
- All decisions must be auditable
- Business rules must be deterministic

## Campaign Flow

1. Briefing Intake
2. Briefing Standardization
3. Briefing Validation
4. Campaign Configuration
5. Scheduling
6. Audience Selection
7. Prioritization
8. Volume Constraints
9. Contact Rules
10. Control Groups
11. Channel Export
12. Deployment

## Coding Standards

- Python 3.12+
- Type hints mandatory
- Pydantic mandatory
- Async FastAPI
- Structured logging
- Unit tests required

## Knowledge Sources

Always consult:

- knowledge/Selection_Briefing_Content_Guide.docx
- knowledge/Framework_Data_Structure.xlsx
- knowledge/Data_Dictionary.xlsx
- knowledge/Database_Model.xlsx
- knowledge/Pega Agentic Migration Plan.docx
- knowledge/Plan for Implementation.docx

Do not invent business rules.
Ask for clarification when business data is missing.