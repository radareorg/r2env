# -*- coding: utf-8 -*-

import argparse
import sys

from r2env.tools import print_console, ERROR
from r2env.core import R2Env


HELP_MESSAGE = """
Usage: r2env [-flags] [action] [args...]

Flags:

  -h, --help    - show this help.
  -v, --version - display r2env version.
  -m, --meson   - use meson instead of acr.
  -p, --package - install the dist package instead of building
  -l, --list    - list available and installed packages

Actions:

  init          - create ~/.r2env directory.
  config        - display current .r2env settings.
  add [pkg]     - build and install given package. See -p and -m
  use [pkg]     - stow a specific version to be the default.
  rm [pkg]      - remove package from ~/.r2env
  path          - show path of current r2 in use.
  list          - list all packages available to r2env.
  shell         - enter a new shell with PATH env var set.
  purge         - remove ~/.r2env

Environment

  R2ENV_PATH    - specify different path other than ~/.r2env

"""


def show_help():
    print_console(HELP_MESSAGE)


def show_version():
    print_console(R2Env().version())


actions_with_argument = ["add", "install", "rm", "uninstall"]
actions_with_arguments = ["sh", "shell", "use"]
actions = {
    "init": R2Env().init,
    "v": show_version,
    "version": show_version,
    "path": R2Env().get_r2_path,
    "sh": R2Env().shell,
    "shell": R2Env().shell,
    "config": R2Env().show_config,
    "ls": R2Env().list_packages,
    "list": R2Env().list_packages,
    "add": R2Env().install,
    "install": R2Env().install,
    "installed": R2Env().list_installed_packages,
    "uninstall": R2Env().uninstall,
    "rm": R2Env().uninstall,
    "use": R2Env().use,
    "purge": R2Env().purge,
    "h": show_help,
    "help": show_help
}


def run_action(argp):
    action = ""
    args = []
    if len(argp.args) > 0:
        action = argp.args[0]
    if len(argp.args) > 1:
        args = argp.args[1:]
    if argp.version:
        print_console(R2Env().version())
    elif argp.list:
        actions["list"]()
    elif action == "":
        show_help()
    elif action not in actions:
        print_console("Invalid action", ERROR)
    elif action in actions_with_arguments:
        actions[action](" ".join(args))
    elif action in actions_with_argument:
        exit_if_not_argument_is_set(args, action)
        actions[action](args[0], use_meson=argp.meson, use_dist=argp.package)
    else:
        actions[action]()


def exit_if_not_argument_is_set(args, action):
    if len(args) < 1:
        if action in ["use", "rm", "uninstall"]:
            print_console("[x] Package not defined.", ERROR)
            R2Env().list_installed_packages()
        else:
            print_console("[x] Missing package argument.", ERROR)
            R2Env().list_available_packages()
        sys.exit(-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("args", help="run specified action. (Run r2env help for more information)",
                        action="store", nargs="*", default=[])
    #parser.add_argument('args', metavar='args', nargs='+', type=str, help='Specified arguments')
    parser.add_argument("-v", "--version", dest="version", help="Show r2env version", action="store_true")
    parser.add_argument("-m", "--meson", dest="meson", help="Use meson instead of acr to compile", action="store_true")
    parser.add_argument("-p", "--package", dest="package", help="Use binary package for target system if available", action="store_true")
    parser.add_argument("-l", "--list", dest="list", help="List available and installed packages", action="store_true")
    parser.print_help = show_help
    argp = parser.parse_args()
    run_action(argp)


if __name__ == "__main__":
    main()
