# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import argparse
from tools import print_console, WARNING, ERROR
import r2env


HELP_MESSAGE = """
Usage: r2env [action] [args...]
Actions:

init               - create .r2env in current directory
config             - display current .r2env settings
install   [pkg]    - build and install given package. Use --meson to use it as the build system.
uninstall [pkg]    - remove selected package
use [pkg]          - use r2 package defined. pkg should be a release version or latest.
version            - show the current Radare version and its origin
versions           - List all Radare versions installed
list               - list all Radare packages available to r2env
shell              - open a new shell with PATH env var set

"""


def run_action(r2e, action, args, use_meson):
    if action == "init":
        r2e.init()
    elif action == "version":
        r2e.r2env_path()
    elif action == "config":
        r2e.show_config()
    elif action == "list":
        r2e.list_available_packages()
    elif action == "config":
        r2e.show_config()
    elif action == "install":
        if len(args) < 1:
            print_console("[x] Missing package argument.", ERROR)
            return
        r2e.install(args[0], use_meson=use_meson)
    elif action == "uninstall":
        if len(args) < 1:
            print_console("[x] Missing package argument.", ERROR)
            return
        r2e.uninstall(args[0])
    elif action == "use":
        if len(args) < 1:
            print_console("[x] Missing package argument.", ERROR)
            return
        r2e.use(args[0])
    elif action == "versions":
        r2e.list_installed_packages()
    elif action == "shell":
        print_console("WIP Command. Stay tunned ;)", WARNING)
        # r2e.enter_shell(args)
    elif action == "help":
        print_console(HELP_MESSAGE)
    else:
        print_console("[X] Action not found", ERROR)
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="run specified action. (Run r2env help for more information)",
                        action="store", default=["help"])
    parser.add_argument('args', metavar='args', nargs='*', type=str, help='Specified arguments')
    parser.add_argument("-v", "--version", help="Show r2env version", action="store_true")
    parser.add_argument("-m", "--meson", help="Use meson as your build system.", action="store_true")
    args = parser.parse_args()
    r2e = r2env.R2Env()
    if args.version:
        print_console(r2e.version())
        return
    run_action(r2e, args.action, args.args, args.meson)


if __name__ == "__main__":
    main()
