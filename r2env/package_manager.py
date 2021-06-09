# -*- coding: utf-8 -*-

import os
import sys
import time

from tools import load_json_file, git_fetch, print_console, ERROR


class PackageManager:

    LOG_DIR = "log"
    PACKAGES_DIR = "versions"
    SOURCE_DIR = "src"

    def __init__(self, r2env_path):
        self._packages = self._load_profiles()
        self._r2env_path = r2env_path

    def list_available_packages(self):
        return self._packages

    def list_installed_packages(self):
        pkg_dir = os.path.join(self._r2env_path, self.PACKAGES_DIR)
        res = []
        if os.path.isdir(pkg_dir):
            for pkg in os.listdir(pkg_dir):
                if os.path.isdir(os.path.join(pkg_dir, pkg)):
                    res.append(pkg)
        return res

    @staticmethod
    def _load_profiles():
        filename = "config/profiles.json"
        profiles = load_json_file(filename)
        if not profiles:
            sys.exit(-1)
        return profiles

    def install_package(self, profile, version):
        logfile = os.path.join(self._r2env_path, self.LOG_DIR, "{}_{}_{}_build.txt".format(profile, version, round(time.monotonic() * 1000)))
        source_path = os.path.join(os.path.join(self._r2env_path, self.SOURCE_DIR, profile))
        dst_dir = os.path.join(os.path.join(self._r2env_path, self.PACKAGES_DIR), "{}@{}".format(profile, version))
        if not os.path.isdir(source_path):
            os.makedirs(source_path)
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        if version not in self._packages[profile]["versions"]:
            print_console("{}@{} package not available. Use 'list' command to see available packages."
                          .format(profile, version), level=ERROR)
            return
        print_console("[-] Downloading {}@{} package".format(profile, version))
        git_fetch(self._packages[profile]["source"], version, source_path)
        print_console("[-] Building package ...")
        success = self._build_from_source(source_path, dst_dir, logfile)
        if success:
            print_console("[*] Package {}@{} installed successfully".format(profile, version))
        else:
            print_console("[x] Something wrong happened during the build process. Check {} for more information.".format(logfile), level=ERROR)
            return

    def _build_from_source(self, source_path, dst_path, logfile):
        """Only works in Unix systems"""
        cmd = "(cd {0} && rm -rf shlr/capstone && ./configure 2>&1 && make -j4 2>&1 && make install DESTDIR={1}) > {2}".format(
            source_path, dst_path, logfile)
        return os.system(cmd) == 0

    def _build_using_meson(self):
        # TODO
        pass
