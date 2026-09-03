#!/usr/bin/env python3
"""Promotion guard for environment transitions."""

from __future__ import annotations

import argparse
import sys

ENV_ORDER = ["DEV", "QA", "UAT", "PROD"]


def normalize(value: str) -> str:
    return value.strip().upper()


def validate_target(environment: str) -> None:
    env = normalize(environment)
    if env not in ENV_ORDER:
        raise ValueError(f"Unsupported environment: {environment}")


def validate_transition(source: str, target: str) -> None:
    source_env = normalize(source)
    target_env = normalize(target)

    if source_env not in ENV_ORDER or target_env not in ENV_ORDER:
        raise ValueError(f"Unsupported transition: {source}->{target}")

    source_idx = ENV_ORDER.index(source_env)
    target_idx = ENV_ORDER.index(target_env)

    if target_idx != source_idx + 1:
        raise ValueError(
            "Invalid promotion. Allowed progression is DEV -> QA -> UAT -> PROD "
            f"(received: {source_env} -> {target_env})."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Environment promotion guard")
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate_target_parser = subcommands.add_parser("validate-target")
    validate_target_parser.add_argument("--environment", required=True)

    validate_transition_parser = subcommands.add_parser("validate-transition")
    validate_transition_parser.add_argument("--source", required=True)
    validate_transition_parser.add_argument("--target", required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "validate-target":
            validate_target(args.environment)
            print(f"Target environment is valid: {normalize(args.environment)}")
        elif args.command == "validate-transition":
            validate_transition(args.source, args.target)
            print(
                "Promotion transition is valid: "
                f"{normalize(args.source)} -> {normalize(args.target)}"
            )
        else:
            parser.error(f"Unsupported command: {args.command}")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
