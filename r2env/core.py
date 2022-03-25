# -*- coding: utf-8 -*-

import os
import shutil

import json
from pathlib import Path
import re

from dploy import stow, unstow

from r2env.exceptions import R2EnvException
from r2env.package_manager import PackageManager
from r2env.tools import print_console, load_json_file, WARNING, ERROR, host_platform


class R2Env:

    VERSION_FILE = "r2_version"

    def __init__(self):
        self._config = self._load_config()
        self._r2env_path = self._config['r2env_path'] if ('r2env_path' in self._config and self._config['r2env_path']) \
            else self._get_default_path()
        self._package_manager = PackageManager(self._r2env_path)

    def init(self):
        if os.path.isdir(self._r2env_path):
            print_console(f"[x] r2env already initialized. Path {self._r2env_path} already exists.", ERROR)
            return
        os.mkdir(self._r2env_path)
        print_console(f"[*] r2env initialized at {self._r2env_path}")

    def get_r2_path(self):
        self.check_if_r2env_initialized()
        r2_version = self._get_current_version()
        r2_path = self._package_manager.get_package_path(r2_version) if r2_version else "Radare package not configured"
        print_console(f" [*] {r2_version} ({r2_path})")

    def show_config(self):
        print_console("[*] Current r2env config:")
        print_console(json.dumps(self._config))

    def list_packages(self):
        self.list_available_packages()
        self.list_installed_packages()

    def list_available_packages(self):
        print_console("- Available")
        packages = self._package_manager.list_available_packages()
        for profile in packages:
            print_console(f"  - {profile}:", WARNING)
            for version in packages[profile]['versions']:
                dists = ", ".join(version['packages'].keys())
                print_console(f" - {profile}@{version['id']}  - {dists}", formatter=1)

    def list_installed_packages(self):
        self.check_if_r2env_initialized()
        print_console("- Installed")
        for pkg in self._package_manager.list_installed_packages():
            if pkg == self._get_current_version():
                print_console(f"  - {pkg} (in use)")
            else:
                print_console(f"  - {pkg}")

    def install(self, package, **kwargs):
        self.check_if_r2env_initialized()
        use_meson = kwargs["use_meson"] if "use_meson" in kwargs else False
        use_dist = kwargs["use_dist"] if "use_dist" in kwargs else False
        if "@" not in package:
            package = f"{package}@git"
        if not self._check_package_format(package):
            raise R2EnvException("[x] Invalid package format.")
        try:
            profile, version = package.split('@')
        except ValueError:
            profile = package
            version = "git"
        self._package_manager.install_package(profile, version, use_meson=use_meson, use_dist=use_dist)
        print_console("[*] Add $HOME/.r2env/bin to your PATH or use 'r2env shell'.")

    def uninstall(self, package, **kwargs):
        self.check_if_r2env_initialized()
        use_dist = kwargs["use_dist"] if "use_dist" in kwargs else False
        if not self._check_package_format(package):
            raise R2EnvException("[x] Invalid package format.")
        self._package_manager.uninstall_package(package, use_dist)

    def purge(self):
        print_console(f"[*] Removing {self._r2env_path}")
        shutil.rmtree(self._r2env_path)

    def use(self, package=None, **_kwargs):
        self.check_if_r2env_initialized()
        if not package:
            self.list_installed_packages()
            raise R2EnvException("Package not defined.")
        if package not in self._package_manager.list_installed_packages():
            raise R2EnvException(f"Package {package} not installed.")
        cur_ver = self._get_current_version()
        new_dst_dir = self._package_manager.get_package_path(package)
        if cur_ver:
            unstow([self._package_manager.get_package_path(cur_ver)], self._r2env_path)
        stow([new_dst_dir], self._r2env_path)
        self._set_current_version(package)
        print_console(f"[*] Using {package} package")

    @staticmethod
    def version():
        thispath = os.path.dirname(os.path.realpath(__file__))
        with open(f"{thispath}/version.txt", "r", encoding="utf-8") as version:
            print_console(version.read())

    def shell(self, cmd=None, **_kwargs):
        bin_path = os.path.join(self._r2env_path, "bin")
        if host_platform() == "windows":
            os.system(f"set PATH={bin_path};%PATH% && cmd")
            return True
        pkgconfig_path = os.path.join(self._r2env_path, "lib", "pkgconfig")
        bin_path = os.path.join(self._r2env_path, "bin")
        export_ps1 = f"export PS1=\"r2env ({self._get_current_version()})\\$ \";"
        export_pkg_config = f"export PKG_CONFIG_PATH=\"{pkgconfig_path}\";"
        export_path = f"export PATH=\"{bin_path}:$PATH\";"
        cmd_shell = "$SHELL -f"
        full_cmd = export_ps1 + export_pkg_config + export_path + cmd_shell
        if host_platform() == "android":  # hack for pre-dtag builds of r2
            library_path = os.path.join(self._r2env_path, "lib")
            full_cmd = f"export LD_LIBRARY_PATH=\"{library_path}\";" + full_cmd
        if host_platform() == "osx":
            library_path = os.path.join(self._r2env_path, "lib")
            # XXX this doesnt work on sip-enabled macs, that's why we use install_name_tool after install
            full_cmd = f"export DYLD_LIBRARY_PATH=\"{library_path}\";" + full_cmd
        if cmd is None:
            return os.system(full_cmd) == 0
        return os.system(f"{full_cmd} -c '{cmd}'") == 0

    @staticmethod
    def _load_config():
        filename = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
        config = load_json_file(filename)
        environment_path = os.getenv("R2ENV_PATH")
        if environment_path is not None:
            config["r2env_path"] = environment_path
        if not config:
            config = {}
        return config

    @staticmethod
    def _get_default_path():
        # TODO: try to find an .r2env starting in current directory
        return os.path.join(Path.home(), ".r2env")

    @staticmethod
    def _check_package_format(package):
        regexp = r"[a-z0-9]+@(\d\.\d\.\d|git)"
        if not package:
            return False
        return re.search(regexp, package) is not None

    def _get_current_version(self):
        version_file = os.path.join(self._r2env_path, self.VERSION_FILE)
        if not os.path.isfile(version_file):
            return ''
        with open(version_file, 'r', encoding="utf-8") as file_desc:
            version = file_desc.read()
        return version

    def _set_current_version(self, package):
        version_file = os.path.join(self._r2env_path, self.VERSION_FILE)
        with open(version_file, 'w', encoding="utf-8") as file_desc:
            file_desc.write(package)

    def check_if_r2env_initialized(self):
        if not os.path.isdir(self._r2env_path):
            raise R2EnvException("Not r2env initialized. Execute 'r2env init' first.")
