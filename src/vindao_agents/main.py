"""CLI entry point for Vindao Agents."""
import argparse
import sys
from pathlib import Path
from vindao_agents import Agent, __version__


def list_agents():
    """List available predefined agents."""
    agents_dir = Path(__file__).parent / "agents"
    if not agents_dir.exists():
        print("No agents directory found.")
        return

    agent_files = sorted(agents_dir.glob("*.md"))
    if not agent_files:
        print("No agents found.")
        return

    print("Available agents:")
    for agent_file in agent_files:
        agent_name = agent_file.stem
        print(f"  - {agent_name}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="agent",
        description="Vindao Agents - An AI agent framework for interactive task automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agent                          # Start chat with DefaultAgent
  agent --agent Developer        # Start chat with Developer agent
  agent --resume abc123          # Resume session with ID abc123
  agent --list                   # List available agents
  agent --version                # Show version
        """
    )

    parser.add_argument(
        "--agent", "-a",
        type=str,
        default="DefaultAgent",
        help="Name of the agent to use (default: DefaultAgent)"
    )

    parser.add_argument(
        "--resume", "-r",
        type=str,
        metavar="SESSION_ID",
        help="Resume a previous session by session ID"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available predefined agents"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"vindao_agents {__version__}"
    )

    args = parser.parse_args()

    # Handle list command
    if args.list:
        list_agents()
        return 0

    # Create agent instance
    try:
        if args.resume:
            print(f"Resuming session: {args.resume}")
            agent = Agent.from_session_id(args.resume)
        else:
            print(f"Loading agent: {args.agent}")
            agent = Agent.from_name(args.agent)

        # Start chat
        agent.chat()
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"\nCouldn't find agent '{args.agent}'. Use --list to see available agents.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nExiting...")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
