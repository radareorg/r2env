# -*- coding: utf-8 -*-

import os
import shutil
import time
from urllib.error import URLError
import zipfile
import json

import wget
import requests

from r2env.exceptions import PackageManagerException
from r2env.tools import load_json_file, git_fetch, git_clean, print_console, ERROR, exit_if_not_exists, host_distname


class PackageManager:
    LOG_DIR = "log"
    PACKAGES_DIR = "versions"
    SOURCE_DIR = "src"
    DOWNLOAD_URL = "https://github.com/radareorg/radare2/releases/download/"

    def __init__(self, r2env_path):
        self._packages = self._load_profiles(r2env_path)
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
    def _load_profiles(r2env_path):
        filename = os.path.join(r2env_path, 'profiles.json')
        # if profiles.json doesn't exist, generate it now
        if not os.path.exists(filename):
            print_console(f"NOTE: {filename} does not exist. Generating it now.")
            PackageManager.update_radare2_profiles(r2env_path)
        profiles = load_json_file(filename)
        if not profiles:
            raise PackageManagerException("No profiles configured.")
        return profiles

    @staticmethod
    def update_radare2_profiles(r2env_path):
        filename = os.path.join(r2env_path, 'profiles.json')
        api_request_url = "https://api.github.com/repos/radareorg/radare2/releases"
        api_request_headers = ["X-GitHub-Api-Version: 2022-11-28", "Accept: application/vnd.github+json"]
        gh_release_info_req = requests.get(api_request_url, {"headers": api_request_headers})
        gh_release_info_req.raise_for_status()  # raise an error if the request got a bad return code
        gh_release_info = gh_release_info_req.json()
        git_version = {'id': 'git', 'packages': {}}
        radare2_versions = [git_version]  # include the git version by default
        for release in gh_release_info:
            release_id = release['tag_name']
            version = {'id': release_id, 'packages': {}}
            # generate a list of downloadable assets for this release that r2env can use
            for asset in release['assets']:
                # note: you're about to see 100 lines of hackery to deal with inconsistent naming schemes
                # the goal is to include as many valid assets as is reasonable without including any that are not valid
                # separate file extension
                asset_name, asset_ext = os.path.splitext(asset['name'])

                # normalize 'seperators' before splitting into components
                asset_ref = asset_name.replace('_', '-').split('-')

                # filter out things like r2ios_sdk and r2blob
                if asset_ref[0] != 'radare2':
                    continue

                # Some assets don't have the version number in the name, which breaks the following processing.
                # None of them are of interest anyway, so just skip them.
                if release_id not in asset_ref:
                    continue

                # remove the beginning 'radare2'
                asset_ref.remove('radare2')

                # we don't need to care about the release id when checking, so remove it
                asset_ref.remove(release_id)

                if asset_ext == '.zip':  # used for Windows builds among other things
                    # if all that remains is w32 or w64, it should be a valid asset for windows
                    if asset_ref == ['w32']:
                        version['packages']['w32'] = asset['name']
                    elif asset_ref == ['w64']:
                        version['packages']['w64'] = asset['name']
                elif asset_ext == '.deb':  # deb package
                    if asset_ref == ['i386']:
                        version['packages']['deb_i386'] = asset['name']
                    elif asset_ref == ['amd64']:
                        version['packages']['deb_x64'] = asset['name']
                elif asset_ext == '.pkg':  # macos bundle
                    # if architecture is unspecified, it's reasonable to assume it's x64
                    if not asset_ref or asset_ref in (['amd64'], ['x64'], ['macos']):
                        version['packages']['mac_x64'] = asset['name']
                    elif asset_ref == ['m1']:
                        version['packages']['mac_arm64'] = asset['name']

            radare2_versions.append(version)

        profiles = {
            'r2frida': {
                'source': 'https://github.com/nowsecure/r2frida',
                'versions': [git_version]
            },
            'r2dec': {
                'source': 'https://github.com/wargio/r2dec-js',
                'versions': [git_version]
            },
            'r2ghidra': {
                'source': 'https://github.com/radareorg/r2ghidra',
                'versions': [git_version]
            },
            'r0': {
                'source': 'https://github.com/radareorg/r0',
                'versions': [git_version]
            },
            'radare2': {
                'source': 'https://github.com/radareorg/radare2',
                'versions': radare2_versions[::-1]
            }
        }
        if not os.path.isdir(r2env_path):
            os.makedirs(r2env_path)
        with open(filename, 'w') as f:
            json.dump(profiles, f)

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
        try:
            wget.download(disturl, pkgfile)
        except (URLError, ConnectionResetError) as err:
            raise PackageManagerException(f"Failed to download {profile} package. Error: {err}") from err
        # TODO: check package checksum
        if dist_name in ("mac_x64", "mac_arm64"):
            return os.system(f"sudo installer -pkg {pkgfile} -target /") == 0
        if dist_name in "w64":
            return self._install_windows_package(pkgfile)
        if dist_name in ("deb_x64", "deb_i386"):
            return os.system(f"sudo dpkg -i {pkgfile}") == 0
        if dist_name in "android":  # termux
            return os.system("apt install radare2") == 0
        raise PackageManagerException(f"Operative System not supported: {os.uname()}")

    def _install_windows_package(self, pkgfile):
        try:
            with zipfile.ZipFile(pkgfile, 'r') as zip_file:
                zip_file.extractall()
                dst_folder = os.path.sep.join([self._r2env_path, "bin"])
                if not os.path.isdir(dst_folder):
                    os.makedirs(dst_folder, 493)  # 0755)
                for file_path in zip_file.namelist():
                    if file_path.endswith(".exe") or file_path.endswith(".dll") and file_path.find("bin") != -1:
                        file_name = os.path.basename(file_path)
                        dst_filepath = os.path.sep.join([dst_folder, file_name])
                        shutil.copyfile(file_path, dst_filepath)
                        print_console(f"[-] Copying {file_path}")
                radare2_bin_file_path = os.path.sep.join([self._r2env_path, "bin", "radare2.exe"])
                r2_bin_file_path = os.path.sep.join([self._r2env_path, "bin", "r2.exe"])
                shutil.copyfile(radare2_bin_file_path, r2_bin_file_path)
                return True
        except (FileNotFoundError, IOError) as err:
            print_console(f"[x] An error occurred when installing {pkgfile}. Error: {err}", level=ERROR)
            self._uninstall_from_dist("radare2", "latest")
            raise PackageManagerException(f"Unable to install Windows package {pkgfile}.") from err

    def _uninstall_from_dist(self, profile, version):
        print_console(f"[*] Cleaning {profile}@{version} package from binary dist")
        dist_name = host_distname()
        if dist_name in "w64":
            dst = os.path.sep.join([self._r2env_path, "bin"])
            print_console(f"[*] Removing {dst}")
            try:
                shutil.rmtree(dst)
                return True
            except OSError as err:
                raise PackageManagerException(f"An issue occurred while removing {dst}. Error: {err}") from err
        if dist_name in ("mac_x64", "mac_arm64"):
            result_code = 0
            pkgname = "org.radare.radare2"
            result_code += os.system("pkgutil --pkg-info " + pkgname)
            result_code += os.system(f"cd / && pkgutil --only-files --files {pkgname} | "
                                     f"tr '\\n' '\\0' | xargs -n 1 -0 sudo rm -f")
            result_code += os.system(f"cd / && pkgutil --only-dirs --files {pkgname} | "
                                     f"tail -r | tr '\\n' '\\0' | xargs -n 1 -0 sudo rmdir 2>/dev/null")
            result_code += os.system(f"sudo pkgutil --forget {pkgname}")
            return result_code == 0
        if dist_name in ("deb_x64", "deb_i386"):
            return os.system("sudo dpkg -r " + profile) == 0
        if dist_name in "android":  # termux
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
        if host_distname() in "w64":
            raise PackageManagerException("acr is not supported on Windows platform. Use meson instead.")
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
        # TODO: ensure source_path logfile or dst_path have no spaces
        cmd = f"(export PKG_CONFIG_PATH=\"{config_path}\";" \
              f"cd \"{source_path}\" && rm -rf build && " \
              f"meson build --buildtype=release --prefix={dst_path} -Dlocal=true 2>&1 && " \
              f"ninja -C build && " \
              f"ninja -C build install) > {logfile} && " \
              f"for a in {dst_path}/bin/* ; do install_name_tool -add_rpath {dst_path}/lib $a ; done"
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
