# -*- coding: utf-8 -*-

import os
import shutil
import sys
import time

from r2env.tools import load_json_file, git_fetch, git_clean, print_console, ERROR, exit_if_not_exists


class PackageManager:

    LOG_DIR = "log"
    PACKAGES_DIR = "versions"
    SOURCE_DIR = "src"

    def __init__(self, r2env_path):
        self._packages = self._load_profiles()
        self._r2env_path = r2env_path

    def get_package_path(self, package_name):
        return os.path.join(self._r2env_path, self.PACKAGES_DIR, package_name)

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
        filename = os.path.join(os.path.dirname(__file__), 'config', 'profiles.json')
        profiles = load_json_file(filename)
        if not profiles:
            sys.exit(-1)
        return profiles

    def install_package(self, profile, version, use_meson):
        log_path = os.path.join(self._r2env_path, self.LOG_DIR)
        logfile = os.path.join(log_path, "{}_{}_{}_build.txt".format(profile, version, round(time.monotonic() * 1000)))
        source_path = os.path.join(os.path.join(self._r2env_path, self.SOURCE_DIR, profile))
        dst_dir = os.path.join(os.path.join(self._r2env_path, self.PACKAGES_DIR), "{}@{}".format(profile, version))
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        if not os.path.isdir(source_path):
            os.makedirs(source_path)
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        self._exit_if_package_not_available(profile, version)
        if self._build_from_source(profile, version, source_path, dst_dir, logfile, use_meson=use_meson):
            print_console("[*] Package {}@{} installed successfully".format(profile, version))
        else:
            print_console("[x] Something wrong happened during the build process. Check {} for more information.".format
                          (logfile), level=ERROR)
            if os.path.isdir(dst_dir):
                shutil.rmtree(dst_dir)

    def uninstall_package(self, package_name):
        pkg_found = False
        for package in self.list_installed_packages():
            if package_name == package:
                pkg_found = True
                pkg_dir = os.path.join(os.path.join(self._r2env_path, self.PACKAGES_DIR), package_name)
                try:
                    shutil.rmtree(pkg_dir)
                    print_console("Removed package {}".format(package_name))
                except OSError as err:
                    print_console("[x] Unable to remove package {0}. Error: {1}".format(package_name, err), ERROR)
                break
        if not pkg_found:
            print_console("[x] Unable to find installed package {0}".format(package_name), ERROR)

    def _build_from_package(self):
        pass

    def _build_from_source(self, profile, version, source_path, dst_path, logfile, use_meson=False):
        exit_if_not_exists(['git'])
        print_console("[*] Installing {}@{} package from source".format(profile, version))
        print_console("[-] Cloning {} version".format(version))
        git_fetch(self._packages[profile]["source"], version, source_path)
        print_console("[-] Cleaning Repo")
        git_clean(source_path)
        if use_meson:
            return self._build_using_meson(source_path, dst_path, logfile)
        return self._build_using_acr(source_path, dst_path, logfile)

    @staticmethod
    def _build_using_acr(source_path, dst_path, logfile):
        """Only works in Unix systems"""
        exit_if_not_exists(['make'])
        print_console("[-] Building package using acr for Termux...")
        extra_flags = ""
        if os.path.isfile("/default.prop"):
            extra_flags = " --with-compiler=termux"
        cmd = "(cd {0} && rm -rf shlr/capstone && ./configure {1}" \
              " --with-rpath --prefix={2} 2>&1 && make -j4 2>&1" \
              "&& make install) > {3}".format(source_path, extra_flags, dst_path, logfile)
        return os.system(cmd) == 0

    @staticmethod
    def _build_using_meson(source_path, dst_path, logfile):
        exit_if_not_exists(['meson', 'ninja'])
        print_console("[-] Building package using meson ...")
        cmd = "(cd {0} && rm -rf build && meson . build --buildtype=release --prefix={1} -Dlocal=true 2>&1" \
              "&& ninja -C build && ninja -C build install) > {2}".format(source_path, dst_path, logfile)
        return os.system(cmd) == 0

    def _exit_if_package_not_available(self, profile, version):
        pkg_found = False
        for available_version in self._packages[profile]["versions"]:
            if available_version['id'] == version:
                pkg_found = True
                break
        if not pkg_found:
            print_console("{}@{} package not available. Use 'list' command to see available packages."
                          .format(profile, version), level=ERROR)
            sys.exit(-1)
