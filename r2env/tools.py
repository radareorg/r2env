# -*- coding: utf-8 -*-

import json
import os
import sys

from shutil import which
from colorama import Fore, Style
from git import Repo


# Global Vars
INFO = 0
WARNING = 1
ERROR = 2


def print_console(msg, level=INFO, formatter=0):
    tabs, color = ["", ""]
    for _ in range(formatter):
        tabs += "    "
    if level == ERROR:
        color = Fore.RED
    elif level == WARNING:
        color = Fore.YELLOW
    print(color + tabs + msg + Style.RESET_ALL)


def host_platform():
    if os.name == "nt":
        return "w64"
    if os.path.isfile("/default.prop"):
        return "android"
    return "unix"


def git_fetch(url, version, source_path):
    if os.path.isdir(os.path.join(source_path, ".git")):
        repo = Repo(source_path)
        repo.remotes.origin.pull("master")
    else:
        repo = Repo.clone_from(url, source_path)
    if version != "latest":
        repo.git.checkout(version)


def git_clean(source_path):
    repo = Repo(source_path)
    repo.git.clean('-xdf')


def exists(tool):
    return which(tool) is not None


def exit_if_not_exists(tools):
    for tool in tools:
        if not exists(tool):
            print_console("[x] {} is required. Please install it first", level=ERROR)
            sys.exit(-1)


def load_json_file(filepath):
    try:
        with open(filepath) as json_file:
            return json.load(json_file)
    except OSError as err:
        print_console("File {} not found. Msg: {}".format(filepath, err), ERROR)
        return None
