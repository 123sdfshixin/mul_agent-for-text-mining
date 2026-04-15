"""Smoke tests for the PepFinder CLI."""

from pepfinder.cli import build_parser


def test_cli_parser_supports_expected_commands() -> None:
    """Ensure the required commands are available."""
    parser = build_parser()
    args = parser.parse_args(["normalize", "input.txt"])
    assert args.command == "normalize"
    args = parser.parse_args(["chunk", "normalized.json"])
    assert args.command == "chunk"
