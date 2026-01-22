from __future__ import annotations

import argparse
import pathlib

from .runner import run_evaluation
from .specs import ChallengeLevel, Framework


def _csv_list(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate apps via chatlas and run Gate 1 + Gate 2 checks "
            "(optionally Gate 3 screenshot grading)."
        )
    )
    parser.add_argument(
        "--frameworks",
        default="streamlit,gradio,shiny,panel,dash",
        help=(
            "Comma-separated frameworks "
            "(default: streamlit,gradio,shiny,panel,dash)"
        ),
    )
    parser.add_argument(
        "--levels",
        default="beginner,intermediate,advanced,expert",
        help=(
            "Comma-separated levels "
            "(default: beginner,intermediate,advanced,expert)"
        ),
    )
    parser.add_argument(
        "--models",
        required=True,
        help="Comma-separated Bedrock model IDs (e.g. us.anthropic....)",
    )
    parser.add_argument("--out", default="runs", help="Output directory")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--base-port", type=int, default=8501)
    parser.add_argument("--aws-region", default=None)
    parser.add_argument("--aws-profile", default=None)
    parser.add_argument("--max-active", type=int, default=4)
    parser.add_argument(
        "--no-gate2",
        action="store_true",
        help="Disable Gate 2",
    )

    parser.add_argument(
        "--gate3",
        action="store_true",
        help=(
            "Enable Gate 3 screenshot grading via inspect-ai. "
            "Requires --gate3-grader-model."
        ),
    )
    parser.add_argument(
        "--gate3-grader-model",
        default=None,
        help=(
            "Inspect model string for the grader (e.g. "
            "anthropic/bedrock/<bedrock-model-id>)."
        ),
    )
    parser.add_argument(
        "--gate3-log-dir",
        default=None,
        help="Where inspect-ai logs should be written (default: logs/gate3)",
    )
    parser.add_argument(
        "--gate3-max-samples",
        type=int,
        default=None,
        help="Limit number of screenshots graded per model (default: all)",
    )

    args = parser.parse_args()

    frameworks = [Framework(v) for v in _csv_list(args.frameworks)]
    levels = [ChallengeLevel(v) for v in _csv_list(args.levels)]
    models = _csv_list(args.models)

    gate3_log_dir = (
        pathlib.Path(args.gate3_log_dir) if args.gate3_log_dir else None
    )

    run_evaluation(
        frameworks=frameworks,
        levels=levels,
        model_ids=models,
        out_dir=pathlib.Path(args.out),
        host=args.host,
        base_port=args.base_port,
        aws_region=args.aws_region,
        aws_profile=args.aws_profile,
        max_active=args.max_active,
        gate2=not args.no_gate2,
        gate3=args.gate3,
        gate3_grader_model=args.gate3_grader_model,
        gate3_log_dir=gate3_log_dir,
        gate3_max_samples=args.gate3_max_samples,
    )


if __name__ == "__main__":
    main()
