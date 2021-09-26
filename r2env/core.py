# -*- coding: utf-8 -*-

import os
import shutil

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
        if os.path.isdir(self._r2env_path):
            print_console("[x] r2env already initialized. Path {} already exists.".format(self._r2env_path), ERROR)
            return
        os.mkdir(self._r2env_path)
        print_console("[*] r2env initialized at {}".format(self._r2env_path))

    def get_r2_path(self):
        self.exit_if_r2env_not_initialized()
        r2_version = self._get_current_version()
        r2_path = self._package_manager.get_package_path(r2_version) if r2_version else "Radare package not configured"
        print_console(" [*] {0} ({1})".format(r2_version, r2_path))

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
            print_console("  - {}:".format(profile), WARNING)
            for version in packages[profile]['versions']:
                dists = ", ".join(version['packages'].keys())
                print_console(" - {}@{}  - {}".format(profile, version['id'], dists), formatter=1)

    def list_installed_packages(self):
        self.exit_if_r2env_not_initialized()
        print_console("- Installed")
        for pkg in self._package_manager.list_installed_packages():
            if pkg == self._get_current_version():
                print_console("  - {} (in use)".format(pkg))
            else:
                print_console("  - {}".format(pkg))

    def install(self, package, use_meson=False, use_dist=False):
        self.exit_if_r2env_not_initialized()
        if not self._check_package_format(package):
            print_console("[x] Invalid package format.", level=ERROR)
            return
        try:
            profile, version = package.split('@')
        except:
            profile = package
            version = "git"
        self._package_manager.install_package(profile, version, use_meson=use_meson, use_dist=use_dist)
        print_console("[*] Add $HOME/.r2env/bin to your PATH or use 'r2env shell'.")

    def uninstall(self, package, use_meson, use_dist):
        self.exit_if_r2env_not_initialized()
        if not self._check_package_format(package):
            print_console("[x] Invalid package format.", level=ERROR)
            return
        self._package_manager.uninstall_package(package, use_dist)

    def purge(self):
        print("Removing " + self._r2env_path)
        shutil.rmtree(self._r2env_path)

    def use(self, package=None):
        self.exit_if_r2env_not_initialized()
        if not package:
            print_console("[x] Package not defined.", ERROR)
            self.list_installed_packages()
            return
        cur_ver = self._get_current_version()
        new_dst_dir = self._package_manager.get_package_path(package)
        if cur_ver:
            unstow([self._package_manager.get_package_path(cur_ver)], self._r2env_path)
        stow([new_dst_dir], self._r2env_path)
        self._set_current_version(package)
        print_console("[*] Using {} package".format(package))

    @staticmethod
    def version():
        thispath = os.path.dirname(os.path.realpath(__file__))
        with open(thispath + "/version.txt", "r") as version:
            return version.read()

    def shell(self, cmd=""):
        if os.name== "nt":
            os.system("set PATH="+self._r2env_path+"\\bin;%PATH% && cmd")
            return True
        line = "export PS1=\"r2env\\$ \";export PKG_CONFIG_PATH=\""
        line = line + self._r2env_path+"/lib/pkgconfig\";export PATH=\""
        line = line + self._r2env_path + "/bin:$PATH\"; $SHELL -f"
        if os.path.isfile("/default.prop"):  # hack for pre-dtag builds of r2
            line = "export LD_LIBRARY_PATH=\"" + self._r2env_path + "/lib\";" + line
        if os.uname().sysname == "Darwin":
            line = "export DYLD_LIBRARY_PATH=\"" + self._r2env_path + "/lib\";" + line
        if cmd.strip() == "":
            return os.system(line)
        return os.system(line + " -c '" + cmd + "'")

    @staticmethod
    def _load_config():
        filename = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
        config = load_json_file(filename)
        ep = os.getenv("R2ENV_PATH")
        if ep is not None:
            config["r2env_path"] = ep
        if not config:
            sys.exit(-1)
        return config

    @staticmethod
    def _get_default_path():
        # TODO: try to find an .r2env starting in current directory
        return os.path.join(Path.home(), ".r2env")

    @staticmethod
    def _check_package_format(package):
        if package == "":
            return True
        return True
        # regexp = re.compile(r"\w+\d@(?:\d\.\d\.\d|git)")
        # return regexp.match(package)

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
