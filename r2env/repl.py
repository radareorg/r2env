# -*- coding: utf-8 -*-

import argparse
import sys

from r2env.tools import print_console, ERROR
from r2env.core import R2Env


HELP_MESSAGE = """
Usage: r2env [action] [args...]
Actions:

init               - create .r2env in current directory
config             - display current .r2env settings
install   [pkg]    - build and install given package. Use --meson to use it as the build system.
uninstall [pkg]    - remove selected package
use [pkg]          - use r2 package defined. pkg should be a release version or latest.
path               - show path of current r2 in use
version            - show version of r2env
versions           - List all Radare versions installed
list               - list all Radare packages available to r2env
shell              - open a new shell with PATH env var set

"""


def show_help():
    print_console(HELP_MESSAGE)


def show_version():
    print_console(R2Env().version())


actions_with_argument = ["install", "uninstall", "use"]
actions_with_arguments = ["shell"]
actions = {
    "init": R2Env().init,
    "version": show_version,
    "path": R2Env().get_r2_path,
    "config": R2Env().show_config,
    "list": R2Env().list_available_packages,
    "install": R2Env().install,
    "shell": R2Env().shell,
    "uninstall": R2Env().uninstall,
    "use": R2Env().use,
    "versions": R2Env().list_installed_packages,
    "help": show_help
}


def run_action(action, args, use_meson):
    if action == "":
        show_help()
    elif action not in actions:
        print_console("[X] Action not found", ERROR)
    elif action in actions_with_arguments:
        actions[action](" ".join(args))
    elif action in actions_with_argument:
        exit_if_not_argument_is_set(args, action)
        if action == "install":
            actions[action](args[0], use_meson=use_meson)
        else:
            actions[action](args[0])
    else:
        actions[action]()


def exit_if_not_argument_is_set(args, action):
    if len(args) < 1:
        if action == "use":
            print_console("[x] Package not defined. Please use 'r2env use' with one installed package. ", ERROR)
            actions["versions"]()
        else:
            print_console("[x] Missing package argument. ( as for example: radare2@latest)", ERROR)
        print_console("[x] Missing package argument. ( as for example: radare2@latest)", ERROR)
        sys.exit(-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="run specified action. (Run r2env help for more information)",
                        action="store", default=["help"])
    parser.add_argument('args', metavar='args', nargs='*', type=str, help='Specified arguments')
    parser.add_argument("-v", "--version", dest="version", help="Show r2env version", action="store_true")
    parser.add_argument("-m", "--meson", dest="meson", help="Use meson as your build system.", action="store_true")
    args = parser.parse_args()
    if args.version:
        print_console(R2Env().version())
        return
    run_action(args.action, args.args, args.meson)


if __name__ == "__main__":
    main()
