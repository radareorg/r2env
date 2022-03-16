# -*- coding: utf-8 -*-

import json
import os

from shutil import which

import git
from colorama import Fore, Style
from git import Repo


from r2env.exceptions import PackageManagerException

INFO = 0
WARNING = 1
ERROR = 2


def print_console(msg, level=INFO, formatter=0):
    tabs, color = ["", ""]
    for _ in range(formatter):
        tabs += "    "
    if os.name == 'nt':
        print(tabs + msg)
        return
    if level == ERROR:
        color = Fore.RED
    elif level == WARNING:
        color = Fore.YELLOW
    print(color + tabs + msg + Style.RESET_ALL)


def host_platform():
    if os.name == "nt":
        return "windows"
    if os.path.isfile("/default.prop"):
        return "android"
    if os.uname().sysname == "Darwin":
        return "osx"
    return "unix"


# TODO :improve to support all archs
def host_distname():  # noqa: C901
    dist_name = None
    try:
        sysname = os.uname().sysname
        machine = os.uname().machine
    except AttributeError:
        sysname = "Windows"
        machine = "amd64"
    if sysname in "Windows" and os.name in "nt":
        dist_name = "w64"
    elif sysname in "Darwin":
        if machine in "x86_64":
            dist_name = "mac_x64"
        if machine in "arm64":
            dist_name = "mac_arm64"
    elif sysname == "Linux":
        if os.path.exists("/usr/bin/dpkg"):
            if machine == "x86_64":
                dist_name = "deb_x64"
            else:
                dist_name = "deb_i386"
    if os.path.isfile("/default.prop"):
        dist_name = "android"
    return dist_name


def git_fetch(url, version, source_path):
    try:
        if os.path.isdir(os.path.join(source_path, ".git")):
            repo = Repo(source_path)
            repo.git.checkout("master")
            repo.remotes.origin.pull("master")
        else:
            repo = Repo.clone_from(url, source_path)
    except git.GitCommandError as err:
        raise PackageManagerException("An error occured clonning the repo. "
                                      f"Verify the source path is not dirty. Error: {err}") \
            from err
    if version != "git":
        repo.git.checkout(version)
    sms = repo.submodules
    for sm in sms:
        if not sm.module_exists():
            sm.update()


def git_clean(source_path):
    repo = Repo(source_path)
    repo.git.clean('-xdf')


def exists(tool):
    return which(tool) is not None


def exit_if_not_exists(tools):
    for tool in tools:
        if not exists(tool):
            raise PackageManagerException(f"[x] {tool} is required. Please install it first")


def load_json_file(filepath):
    try:
        with open(filepath, encoding="utf-8") as json_file:
            return json.load(json_file)
    except OSError as err:
        print_console(f"File {filepath} not found. Msg: {err}", ERROR)
        return None
