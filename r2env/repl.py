# -*- coding: utf-8 -*-

import argparse
import sys

from r2env.exceptions import ActionException, R2EnvException, PackageManagerException
from r2env.tools import print_console, ERROR
from r2env.core import R2Env


class REPL:
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

    def __init__(self):
        self.actions_with_arguments = ["add", "install", "rm", "uninstall", "use"]
        self._core = R2Env()
        self.actions = {
            "init": self._core.init,
            "v": self._core.version,
            "version": self._core.version,
            "path": self._core.get_r2_path,
            "sh": self._core.shell,
            "shell": self._core.shell,
            "config": self._core.show_config,
            "ls": self._core.list_packages,
            "list": self._core.list_packages,
            "add": self._core.install,
            "install": self._core.install,
            "installed": self._core.list_installed_packages,
            "uninstall": self._core.uninstall,
            "rm": self._core.uninstall,
            "use": self._core.use,
            "purge": self._core.purge,
            "h": self.show_help,
            "help": self.show_help
        }

    def show_help(self):
        print_console(self.HELP_MESSAGE)

    def run_action(self, action_args):  # noqa: C901
        args = []
        if not action_args:
            self.show_help()
            raise ActionException("No action selected")
        if action_args.version:
            self.actions["version"]()
            return
        if action_args.list:
            list_method = self.actions["list"]
            list_method()
        if len(action_args.args) == 0:
            self.show_help()
            raise ActionException("No action selected")
        if len(action_args.args) > 1:
            args = action_args.args[1:]
        action = action_args.args[0]
        if action not in self.actions:
            raise ActionException("Invalid action selected")
        if len(args) < 1 and action in self.actions_with_arguments:
            if action in ["add", "install"]:
                self._core.list_packages()
            if action in ["use", "rm", "uninstall"]:
                self._core.list_installed_packages()
            raise ActionException(f"Action {action} requires a package as an argument.")
        if action in self.actions_with_arguments:
            self.actions[action](args[0], use_meson=action_args.meson, use_dist=action_args.package)
        elif action in "shell" and len(args) > 0:
            self.actions[action](args[0])
        else:
            self.actions[action]()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("args", help="run specified action. (Run r2env help for more information)",
                        action="store", nargs="*", default=[])
    # parser.add_argument('args', metavar='args', nargs='+', type=str, help='Specified arguments')
    parser.add_argument("-v", "--version", dest="version", help="Show r2env version", action="store_true")
    parser.add_argument("-m", "--meson", dest="meson", help="Use meson instead of acr to compile", action="store_true")
    parser.add_argument("-p", "--package", dest="package", help="Use binary package for target system if available",
                        action="store_true")
    parser.add_argument("-l", "--list", dest="list", help="List available and installed packages", action="store_true")
    parser.print_help = REPL().show_help
    action_args = parser.parse_args()
    try:
        REPL().run_action(action_args)
    except ActionException as err:
        print_console(f"[x] Parameter error. Details: {err}", level=ERROR)
        sys.exit(-1)
    except PackageManagerException as err:
        print_console(f"[x] Package Error: {err}", level=ERROR)
        sys.exit(-1)
    except R2EnvException as err:
        print_console(f"[x] r2Env Error: {err}", level=ERROR)
        sys.exit(-1)


if __name__ == "__main__":
    main()
