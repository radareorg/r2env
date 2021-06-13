# -*- coding: utf-8 -*-

import os
import sys

from colorama import Fore, Style
from git import Repo
from shutil import which
import json


# Global Vars
INFO = 0
WARNING = 1
ERROR = 2


def print_console(msg, level=INFO, formatter=0):
    tabs, color = ["", ""]
    for i in range(formatter):
        tabs += "    "
    if level == ERROR:
        color = Fore.RED
    elif level == WARNING:
        color = Fore.YELLOW
    print(color + tabs + msg + Style.RESET_ALL)


def host_platform():
    if os.name == "nt":
        return "w64"
    if os.file.exists("/default.prop"):
        return "android"
    return "unix"


def git_fetch(url, version, dst_dir):
    if os.path.isdir(dst_dir):
        repo = Repo(dst_dir)
        repo.remotes.origin.pull("master")
    else:
        repo = Repo.clone_from(url, dst_dir)
    if version != "latest":
        repo.git.checkout(version)
    return


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
    except Exception as err:
        print_console("File {} not found. Msg: {}".format(filepath, err), ERROR)
        return None
