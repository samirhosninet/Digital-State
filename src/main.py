import sys
from digital_state.cli.cli import run_cli


def main():
    """Main CLI entry point mapping calls to the run execution utility."""
    sys.exit(run_cli(sys.argv[1:]))


if __name__ == "__main__":
    main()
