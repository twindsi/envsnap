"""Integration hook to register the schedule subcommand into the main CLI."""

from envsnap.cli_schedule import add_schedule_subparser, cmd_schedule


def register(subparsers, command_map: dict, snapshot_dir_getter) -> None:
    """Register the 'schedule' command.

    Args:
        subparsers: argparse subparsers action from the main parser.
        command_map: dict mapping command name -> handler callable.
        snapshot_dir_getter: zero-arg callable returning the snapshot directory path.
    """
    add_schedule_subparser(subparsers)

    def _handler(args):
        cmd_schedule(args, snapshot_dir_getter())

    command_map["schedule"] = _handler
