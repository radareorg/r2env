# -*- coding: utf-8 -*-

import os
import re

import json
import sys
from pathlib import Path
from dploy import stow, unstow
from r2env.package_manager import PackageManager
from r2env.tools import print_console, load_json_file, WARNING, ERROR


class R2Env:

    VERSION_FILE = "r2_version"

    def __init__(self):
        self._config = self._load_config()
        self._r2env_path = self._config['r2env_path'] if ('r2env_path' in self._config and self._config['r2env_path']) \
            else self._get_default_path()
        self._package_manager = PackageManager(self._r2env_path)

    def init(self):
        r2env_full_path = os.path.join(self._r2env_path, ".r2env")
        if os.path.isdir(r2env_full_path):
            print_console("[x] r2env already initialized. Path {} already exists.".format(r2env_full_path), ERROR)
            return
        os.mkdir(r2env_full_path)
        print_console("[*] r2env initialized at {}".format(r2env_full_path))

    def get_r2_path(self):
        self.exit_if_r2env_not_initialized()
        r2_version = self._get_current_version()
        r2_path = self._package_manager.get_package_path(r2_version) if r2_version else "Radare package not configured"
        print_console(" [*] {0} ({1})".format(r2_version, r2_path))

    def show_config(self):
        return json.dumps(self._config)

    def list_available_packages(self):
        print_console("[*] List of available Radare packages")
        packages = self._package_manager.list_available_packages()
        for profile in packages:
            print_console("  - {} packages:".format(profile), WARNING)
            for version in packages[profile]['versions']:
                print_console(" {}@{}".format(profile, version['id']), formatter=1)

    def list_installed_packages(self):
        self.exit_if_r2env_not_initialized()
        print_console("[*] Installed Radare packages")
        for pkg in self._package_manager.list_installed_packages():
            if pkg == self._get_current_version():
                print_console("  [*] {}".format(pkg))
            else:
                print_console("  - {}".format(pkg))

    def install(self, package, use_meson=False):
        self.exit_if_r2env_not_initialized()
        if not self._check_package_format(package):
            print_console("[x] Invalid Package format.", level=ERROR)
            return
        profile, version = package.split('@')
        self._package_manager.install_package(profile, version, use_meson=use_meson)
        print_console("[*] Magic Done! Remember to add the $HOME/.r2env/bin folder to your PATH.")

    def uninstall(self, package):
        self.exit_if_r2env_not_initialized()
        if not self._check_package_format(package):
            print_console("[x] Invalid Package format.", level=ERROR)
            return
        self._package_manager.uninstall_package(package)

    def use(self, package):
        self.exit_if_r2env_not_initialized()
        cur_ver = self._get_current_version()
        new_dst_dir = self._package_manager.get_package_path(package)
        if cur_ver:
            unstow([self._package_manager.get_package_path(cur_ver)], self._r2env_path)
        stow([new_dst_dir], self._r2env_path)
        self._set_current_version(package)
        print_console("[*] Using {} package".format(package))

    @staticmethod
    def version():
        with open("version.txt", "r") as version:
            return version.read()

    def shell(self):
        pass

    @staticmethod
    def _load_config():
        filename = os.path.join(sys.prefix, "config/config.json")
        config = load_json_file(filename)
        if not config:
            sys.exit(-1)
        return config

    @staticmethod
    def _get_default_path():
        return os.path.join(Path.home(), ".r2env")

    @staticmethod
    def _check_package_format(package):
        regexp = re.compile(r"\w+\d@[\d\.\d\.\d,'latest']")
        return regexp.match(package)

    def _get_current_version(self):
        version_file = os.path.join(self._r2env_path, self.VERSION_FILE)
        if not os.path.isfile(version_file):
            return ''
        with open(version_file, 'r') as file_desc:
            version = file_desc.read()
        return version

    def _set_current_version(self, package):
        version_file = os.path.join(self._r2env_path, self.VERSION_FILE)
        with open(version_file, 'w') as file_desc:
            file_desc.write(package)

    def exit_if_r2env_not_initialized(self):
        if not os.path.isdir(self._r2env_path):
            print_console("Not r2env initialized. Execute 'r2env init' first.", ERROR)
            sys.exit(-1)
