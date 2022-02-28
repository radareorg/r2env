# -*- coding: utf-8 -*-

import os
import shutil
import time
from zipfile import ZipFile

import wget

from r2env.exceptions import PackageManagerException
from r2env.tools import load_json_file, git_fetch, git_clean, print_console, ERROR, exit_if_not_exists, host_distname


class PackageManager:
    LOG_DIR = "log"
    PACKAGES_DIR = "versions"
    SOURCE_DIR = "src"
    DOWNLOAD_URL = "https://github.com/radareorg/radare2/releases/download/"

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
            raise PackageManagerException("No profiles configured.")
        return profiles

    def install_package(self, profile, version, use_meson, use_dist):
        log_path = os.path.join(self._r2env_path, self.LOG_DIR)
        timestamp = round(time.monotonic() * 1000)
        logfile = os.path.join(log_path, f"{profile}_{version}_{timestamp}_build.txt")
        source_path = os.path.join(os.path.join(self._r2env_path, self.SOURCE_DIR, profile))
        dst_dir = os.path.join(os.path.join(self._r2env_path, self.PACKAGES_DIR), f"{profile}@{version}")
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        if not os.path.isdir(source_path):
            os.makedirs(source_path)
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        self._exit_if_package_not_available(profile, version)
        if use_dist:
            if self._install_from_dist(profile, version):
                print_console(f"[*] Binary package {profile}@{version} installed successfully")
            else:
                raise PackageManagerException(f"[x] Failed to install {profile}@{version}.")
        else:
            if self._build_from_source(profile, version, source_path, dst_dir, logfile, use_meson=use_meson):
                print_console(f"[*] Package {profile}@{version} installed successfully")
            else:
                if os.path.isdir(dst_dir):
                    shutil.rmtree(dst_dir)
                raise PackageManagerException(f"[x] Failed to build {profile}@{version}. "
                                              f"Check {logfile} for more information.")

    def uninstall_package(self, package_name, use_dist):
        pkg_found = False
        for package in self.list_installed_packages():
            if package_name == package:
                pkg_found = True
                if use_dist:
                    profile, version = package.split("@")
                    self._uninstall_from_dist(profile, version)
                else:
                    pkg_dir = os.path.join(self._r2env_path, self.PACKAGES_DIR, package)
                    try:
                        shutil.rmtree(pkg_dir)
                        print_console(f"[-] Removed package {package_name}")
                    except OSError as err:
                        raise PackageManagerException(f"[x] Unable to remove package {package_name}. Error: {err}") \
                            from err
                break
        if not pkg_found:
            raise PackageManagerException(f"[x] Unable to find installed package {package_name}")

    def _get_pkgname(self, profile, version, cos):
        for pkgv in self._packages[profile]["versions"]:
            if pkgv["id"] == version:
                for pkgd in pkgv["packages"].keys():
                    if pkgd == cos:
                        return pkgv["packages"][pkgd]
        return None

    def _get_disturl(self, profile, version, cos):
        pkgname = self._get_pkgname(profile, version, cos)
        if pkgname is not None:
            return "/".join([self.DOWNLOAD_URL, version, pkgname])
        return None

    def _install_from_dist(self, profile, version):
        print_console(f"[*] Installing {profile}@{version} package from binary dist")
        dist_name = host_distname()
        disturl = self._get_disturl(profile, version, dist_name)
        pkgname = self._get_pkgname(profile, version, dist_name)
        pkgfile = "/".join([self._r2env_path, "src", pkgname])
        wget.download(disturl, pkgfile)
        sysname = host_distname()
        # TODO: check package checksum
        if sysname in "Darwin":
            return os.system(f"sudo installer -pkg {pkgfile} -target /") == 0
        if sysname in "w64":
            return self._install_windows_package(pkgfile)
        if sysname in "deb_x64" or sysname in "deb_i386":
            return os.system(f"sudo dpkg -i {pkgfile}") == 0
        if sysname in "android":  # termux
            return os.system("apt install radare2") == 0
        raise PackageManagerException(f"Operative System not supported: {os.uname()}")

    def _install_windows_package(self, pkgfile):
        with ZipFile(pkgfile, 'r') as zip_file:
            zip_file.extractall()
            dst = os.path.sep.join([self._r2env_path, "bin"])
            try:
                for filename in zip_file.namelist():
                    if filename.endswith(".exe") or filename.endswith(".dll") and filename.find("bin") != -1:
                        fname = os.path.basename(filename)
                        d = os.path.sep.join([dst, fname])
                        dname = os.path.dirname(d)
                        if not os.path.isdir(dname):
                            os.makedirs(dname, 493)  # 0755)
                        shutil.copyfile(filename, d)
                        print_console(filename)
                radare2_bin_file_path = os.path.sep.join([self._r2env_path, "bin", "radare2.exe"])
                r2_bin_file_path = os.path.sep.join([self._r2env_path, "bin", "r2.exe"])
                shutil.copyfile(radare2_bin_file_path, r2_bin_file_path)
                return True
            except IOError as err:
                print_console(f"[x] Unable to copy file {err}", level=ERROR)
                self._uninstall_from_dist("radare2", "latest")
        raise PackageManagerException(f"An error occurred when installing {pkgfile}.")

    def _uninstall_from_dist(self, profile, version):
        print_console(f"[*] Cleaning {profile}@{version} package from binary dist")
        sysname = host_distname()
        if sysname == "Windows":
            dst = os.path.sep.join([self._r2env_path, "bin"])
            shutil.rmtree(dst)
        if sysname == "Darwin":
            pkgname = "org.radare.radare2"
            os.system("pkgutil --pkg-info " + pkgname)
            os.system(f"cd / && pkgutil --only-files --files {pkgname} | "
                      f"tr '\\n' '\\0' | xargs -n 1 -0 sudo rm -f")
            os.system(f"cd / && pkgutil --only-dirs --files {pkgname} | "
                      f"tail -r | tr '\\n' '\\0' | xargs -n 1 -0 sudo rmdir 2>/dev/null")
            os.system(f"sudo pkgutil --forget {pkgname}")
        if sysname in ("deb_x64", "deb_i386"):
            return os.system("sudo dpkg -r " + profile) == 0
        if sysname == "android":  # termux
            return os.system("sudo dpkg -r radare2") == 0
        raise PackageManagerException(f"Operative System not supported: {os.uname()}")

    def _build_from_source(self, profile, version, source_path, dst_path, logfile, use_meson=False):
        exit_if_not_exists(['git'])
        print_console(f"[*] Installing {profile}@{version} package from source")
        print_console(f"[-] Cloning {version} version")
        git_fetch(self._packages[profile]["source"], version, source_path)
        print_console("[-] Cleaning Repo")
        git_clean(source_path)
        if use_meson:
            return self._build_using_meson(source_path, dst_path, logfile, self._r2env_path)
        return self._build_using_acr(source_path, dst_path, logfile, self._r2env_path)

    @staticmethod
    def _build_using_acr(source_path, dst_path, logfile, r2env_path):
        """Only works in Unix systems"""
        exit_if_not_exists(['make'])
        print_console("[-] Building package using acr...")
        extra_flags = ""
        if os.path.isfile("/default.prop"):
            extra_flags = " --with-compiler=termux"
        config_path = r2env_path + "/lib/pkgconfig"
        cmd = f"(export PKG_CONFIG_PATH=\"{config_path}\";" \
              f"cd {source_path} && " \
              f"rm -rf shlr/capstone && " \
              f"./configure {extra_flags} --with-rpath --prefix={dst_path} 2>&1 && " \
              f"make -j4 2>&1 && " \
              f"make install) > {logfile}"
        print_console(f"Executing {cmd}")
        return os.system(cmd) == 0

    @staticmethod
    def _build_using_meson(source_path, dst_path, logfile, r2env_path):
        exit_if_not_exists(['meson', 'ninja'])
        print_console("[-] Building package using meson ...")
        config_path = r2env_path + "/lib/pkgconfig"
        cmd = f"(export PKG_CONFIG_PATH=\"{config_path}\";" \
              f"cd {source_path} && rm -rf build && " \
              f"meson . build --buildtype=release --prefix={dst_path} -Dlocal=true 2>&1 && " \
              f"ninja -C build && " \
              f"ninja -C build install) > {logfile}"
        print_console(f"Executing {cmd}")
        return os.system(cmd) == 0

    def _exit_if_package_not_available(self, profile, version):
        pkg_found = False
        for available_version in self._packages[profile]["versions"]:
            if available_version['id'] == version:
                pkg_found = True
                break
        if not pkg_found:
            raise PackageManagerException(
                f"{profile}@{version} package not available. Use 'list' command to see available packages.")
