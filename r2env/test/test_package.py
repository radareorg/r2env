import os
from unittest.mock import MagicMock
from urllib.error import URLError

from doublex import assert_that
from hamcrest import equal_to
from mock import patch
import unittest

from r2env.exceptions import PackageManagerException
from r2env.package_manager import PackageManager


class TestPackageManager(unittest.TestCase):
    def setUp(self):
        self.profile = "radare2"
        self.version = "5.3.0"
        self.profiles = {
            self.profile: {
                "source": "https://github.com/radareorg/radare2",
                "versions": [
                    {
                        "id": self.version,
                        "packages": {
                            "w64": "radare2-5.3.0-w64.zip",
                            "deb_x64": "radare2_5.3.0_amd64.deb"
                        }
                    }
                ]
            }
        }
        self.load_json_mock = patch("r2env.package_manager.load_json_file").start()
        self.load_json_mock.return_value = self.profiles
        self.default_r2env_path = "/tmp/r2env"
        self.package_manager = PackageManager(self.default_r2env_path)

    def tearDown(self):
        patch.stopall()

    def test_constructor(self):
        assert_that(self.package_manager._packages, equal_to(self.profiles))
        assert_that(self.package_manager._r2env_path, equal_to(self.default_r2env_path))

    def test_constructor_with_no_profiles(self):
        self.load_json_mock.return_value = []
        with self.assertRaises(PackageManagerException):
            PackageManager(self.default_r2env_path)

    def test_get_package_path(self):
        package_name = "test"
        package_path = self.package_manager.get_package_path(package_name)
        assert_that(package_path, equal_to(os.path.join(self.default_r2env_path, "versions", package_name)))

    def test_list_available_packages(self):
        assert_that(self.package_manager.list_available_packages(), equal_to(self.profiles))

    @patch("r2env.package_manager.os")
    def test_list_installed_packages(self, os_mock):
        packages = ["PKG1", "PKG2", "PKG3"]
        os_mock.path.isdir.return_value = True
        os_mock.listdir.return_value = packages
        assert_that(self.package_manager.list_installed_packages(), equal_to(packages))

    @patch("r2env.package_manager.os.makedirs")
    @patch("r2env.package_manager.os.path.isdir")
    def test_install_package_with_no_log_path(self, mock_isdir, mock_makedirs):
        patch("r2env.package_manager.PackageManager._build_from_source").start()
        patch("r2env.package_manager.PackageManager._install_from_dist").start()
        mock_isdir.side_effect = [False, True, True]
        self.package_manager.install_package(self.profile, self.version, True, True)
        mock_makedirs.assert_called_once()

    @patch("r2env.package_manager.os.makedirs")
    @patch("r2env.package_manager.os.path.isdir")
    def test_install_package_with_no_source_path(self, mock_isdir, mock_makedirs):
        patch("r2env.package_manager.PackageManager._build_from_source").start()
        patch("r2env.package_manager.PackageManager._install_from_dist").start()
        mock_isdir.side_effect = [True, False, True]
        self.package_manager.install_package(self.profile, self.version, True, True)
        source_path = os.path.join(os.path.join(self.package_manager._r2env_path,
                                                self.package_manager.SOURCE_DIR, self.profile))
        mock_makedirs.assert_called_once_with(source_path)

    @patch("r2env.package_manager.os.makedirs")
    @patch("r2env.package_manager.os.path.isdir")
    def test_install_package_with_no_dstdir(self, mock_isdir, mock_makedirs):
        patch("r2env.package_manager.PackageManager._build_from_source").start()
        patch("r2env.package_manager.PackageManager._install_from_dist").start()
        mock_isdir.side_effect = [True, True, False]
        self.package_manager.install_package(self.profile, self.version, True, True)
        dst_dir = os.path.join(self.package_manager._r2env_path,
                               self.package_manager.PACKAGES_DIR,
                               f"{self.profile}@{self.version}")
        mock_makedirs.assert_called_once_with(dst_dir)

    @patch("r2env.package_manager.PackageManager._install_from_dist")
    @patch("r2env.package_manager.os.path.isdir")
    def test_install_package_from_dist_success(self, mock_isdir,
                                               mock_dist):
        mock_isdir.return_value = True
        mock_dist.return_value = True
        self.package_manager.install_package(self.profile, self.version, True, True)
        mock_dist.assert_called_once_with(self.profile, self.version)

    @patch("r2env.package_manager.PackageManager._install_from_dist")
    @patch("r2env.package_manager.os.path.isdir")
    def test_install_package_from_dist_failed(self, mock_isdir,
                                              mock_dist):
        mock_isdir.return_value = True
        mock_dist.return_value = False
        with self.assertRaises(PackageManagerException):
            self.package_manager.install_package(self.profile, self.version, True, True)
        mock_dist.assert_called_once_with(self.profile, self.version)

    @patch("r2env.package_manager.PackageManager._build_from_source")
    @patch("r2env.package_manager.os.path.isdir")
    def test_install_package_from_build_success(self, mock_isdir,
                                                mock_build):
        mock_isdir.return_value = True
        mock_build.return_value = True
        self.package_manager.install_package(self.profile, self.version, True, False)
        mock_build.assert_called_once()

    @patch("r2env.package_manager.shutil.rmtree")
    @patch("r2env.package_manager.PackageManager._build_from_source")
    @patch("r2env.package_manager.os.path.isdir")
    def test_install_package_from_build_failed(self, mock_isdir,
                                                mock_build, mock_rmtree):
        mock_isdir.return_value = True
        mock_build.return_value = False
        with self.assertRaises(PackageManagerException):
            self.package_manager.install_package(self.profile, self.version, True, False)
        mock_build.assert_called_once()
        mock_rmtree.assert_called_once()

    @patch("r2env.package_manager.PackageManager.list_installed_packages")
    @patch("r2env.package_manager.PackageManager._uninstall_from_dist")
    def test_uninstall_package_from_dist_successfully(self, mock_uninstall, mock_list_pkg):
        mock_list_pkg.return_value = ["radare2@1.0.0", "radare2@2.0.0"]
        profile = "radare2"
        version = "2.0.0"
        package = f"{profile}@{version}"
        self.package_manager.uninstall_package(package, True)
        mock_uninstall.assert_called_once_with(profile, version)

    @patch("r2env.package_manager.PackageManager.list_installed_packages")
    @patch("r2env.package_manager.shutil.rmtree")
    def test_uninstall_package_from_build_successfully(self, mock_rmtree, mock_list_pkg):
        mock_list_pkg.return_value = ["radare2@1.0.0", "radare2@2.0.0"]
        package = "radare2@2.0.0"
        self.package_manager.uninstall_package(package, False)
        pkg_dir = os.path.join(self.package_manager._r2env_path,
                               self.package_manager.PACKAGES_DIR,
                               package)
        mock_rmtree.assert_called_once_with(pkg_dir)

    @patch("r2env.package_manager.PackageManager.list_installed_packages")
    @patch("r2env.package_manager.shutil.rmtree")
    def test_uninstall_package_from_build_failed(self, mock_rmtree, mock_list_pkg):
        mock_list_pkg.return_value = ["radare2@1.0.0", "radare2@2.0.0"]
        package = "radare2@2.0.0"
        mock_rmtree.side_effect = OSError("fail")
        with self.assertRaises(PackageManagerException):
            self.package_manager.uninstall_package(package, False)

    @patch("r2env.package_manager.PackageManager.list_installed_packages")
    def test_uninstall_package_not_found(self, mock_list_pkg):
        mock_list_pkg.return_value = ["radare2@1.0.0"]
        package = "radare2@2.0.0"
        with self.assertRaises(PackageManagerException):
            self.package_manager.uninstall_package(package, False)

    def test_get_pkgname_success(self):
        target_pkg = "radare2-5.3.1-w64.zip"
        target_os = "w64"
        target_version = "5.3.1"
        packages_mock = {"radare2": {
            "versions": [
            {
                "id": "5.3.0",
                "packages": {
                  "w64": "radare2-5.3.0-w64.zip",
                }
            },
            {
                "id": target_version,
                "packages": {
                  target_os: target_pkg,
                  "mac_x64": "radare2-5.3.1.pkg",
                }
            }]
        }}
        self.package_manager._packages = packages_mock
        assert_that(self.package_manager._get_pkgname("radare2", target_version, target_os), equal_to(target_pkg))

    def test_get_pkgname_failed(self):
        target_os = "w64"
        target_version = "5.3.1"
        packages_mock = {"radare2": {
            "versions": [
            {
                "id": "5.3.0",
                "packages": {
                  "w64": "radare2-5.3.0-w64.zip",
                }
            },
        ]
        }}
        self.package_manager._packages = packages_mock
        assert_that(self.package_manager._get_pkgname("radare2", target_version, target_os), equal_to(None))

    @patch("r2env.package_manager.PackageManager._get_pkgname")
    def test_get_disturl_success(self, mock_getpkg):
        target_pkg = "radare2-5.3.1-w64.zip"
        version = "5.2.0"
        mock_getpkg.return_value = target_pkg
        dist_url = self.package_manager._get_disturl("mock_profile", version, "mock_cos")
        expected_url = "/".join([self.package_manager.DOWNLOAD_URL, version, target_pkg])
        assert_that(dist_url, equal_to(expected_url))

    @patch("r2env.package_manager.PackageManager._get_pkgname")
    def test_get_disturl_failed(self, mock_getpkg):
        target_pkg = None
        mock_getpkg.return_value = target_pkg
        dist_url = self.package_manager._get_disturl("mock_profile", "mock_version", "mock_cos")
        assert_that(dist_url, equal_to(None))

    @patch("r2env.package_manager.wget")
    @patch("r2env.package_manager.PackageManager._get_pkgname")
    @patch("r2env.package_manager.PackageManager._get_disturl")
    @patch("r2env.package_manager.host_distname")
    def test_install_from_dist_wget_is_called(self, mock_host_distname,
                                              mock__get_disturl,
                                              mock__get_pkgname,
                                              mock_wget):
        patch("r2env.package_manager.os.system").start()
        pkgname = "radare2-5.3.1-w64.zip"
        disturl = "http://example.org"
        pkgfile = "/".join([self.package_manager._r2env_path, "src", pkgname])
        mock__get_pkgname.return_value = pkgname
        mock__get_disturl.return_value = disturl
        mock_host_distname.return_value = "mac_arm64"
        profile = "radare2"
        version = "5.6.0"
        self.package_manager._install_from_dist(profile, version)
        mock_wget.download.assert_called_once_with(disturl, pkgfile)

    @patch("r2env.package_manager.wget")
    def test_install_from_dist_wget_error_url(self, mock_wget):
        pkgname_mock = patch("r2env.package_manager.PackageManager._get_pkgname").start()
        get_disturl_mock = patch("r2env.package_manager.PackageManager._get_disturl").start()
        pkgname_mock.return_value = "radare2-5.3.1-w64.zip"
        get_disturl_mock.return_value = "http://example.org"
        mock_wget.download.side_effect = URLError("error")
        with self.assertRaises(PackageManagerException):
            self.package_manager._install_from_dist("profile", "version")

    @patch("r2env.package_manager.wget")
    def test_install_from_dist_wget_error_connection(self, mock_wget):
        pkgname_mock = patch("r2env.package_manager.PackageManager._get_pkgname").start()
        get_disturl_mock = patch("r2env.package_manager.PackageManager._get_disturl").start()
        pkgname_mock.return_value = "radare2-5.3.1-w64.zip"
        get_disturl_mock.return_value = "http://example.org"
        mock_wget.download.side_effect = ConnectionResetError("error")
        with self.assertRaises(PackageManagerException):
            self.package_manager._install_from_dist("profile", "version")

    @patch("r2env.package_manager.wget")
    def test_install_from_dist_wget_error_connection(self, mock_wget):
        pkgname_mock = patch("r2env.package_manager.PackageManager._get_pkgname").start()
        get_disturl_mock = patch("r2env.package_manager.PackageManager._get_disturl").start()
        pkgname_mock.return_value = "radare2-5.3.1-w64.zip"
        get_disturl_mock.return_value = "http://example.org"
        mock_wget.download.side_effect = ConnectionResetError("error")
        with self.assertRaises(PackageManagerException):
            self.package_manager._install_from_dist("profile", "version")

    @patch("r2env.package_manager.os.system")
    @patch("r2env.package_manager.PackageManager._get_pkgname")
    @patch("r2env.package_manager.PackageManager._get_disturl")
    @patch("r2env.package_manager.host_distname")
    def test_install_from_dist_mac(self, mock_host_distname,
                                   mock__get_disturl,
                                   mock__get_pkgname,
                                   mock_system):
        pkgname = "radare2-5.3.1-mac.pkg"
        pkgfile = "/".join([self.package_manager._r2env_path, "src", pkgname])
        mock__get_pkgname.return_value = pkgname
        mock__get_disturl.return_value = "http://example.org"
        mock_host_distname.return_value = "mac_arm64"
        profile = "radare2"
        version = "5.6.0"
        patch("r2env.package_manager.wget.download").start()
        mock_system.return_value = 0
        assert_that(self.package_manager._install_from_dist(profile, version), equal_to(True))
        mock_system.assert_called_once_with(f"sudo installer -pkg {pkgfile} -target /")

    @patch("r2env.package_manager.os.system")
    @patch("r2env.package_manager.PackageManager._get_pkgname")
    @patch("r2env.package_manager.PackageManager._get_disturl")
    @patch("r2env.package_manager.host_distname")
    def test_install_from_dist_linux_deb(self, mock_host_distname,
                                   mock__get_disturl,
                                   mock__get_pkgname,
                                   mock_system):
        pkgname = "radare2-5.3.1-linux.deb"
        pkgfile = "/".join([self.package_manager._r2env_path, "src", pkgname])
        mock__get_pkgname.return_value = pkgname
        mock__get_disturl.return_value = "http://example.org"
        mock_host_distname.return_value = "deb_x64"
        profile = "radare2"
        version = "5.6.0"
        patch("r2env.package_manager.wget.download").start()
        mock_system.return_value = 0
        assert_that(self.package_manager._install_from_dist(profile, version), equal_to(True))
        mock_system.assert_called_once_with(f"sudo dpkg -i {pkgfile}")

    @patch("r2env.package_manager.os.system")
    @patch("r2env.package_manager.PackageManager._get_pkgname")
    @patch("r2env.package_manager.PackageManager._get_disturl")
    @patch("r2env.package_manager.host_distname")
    def test_install_from_dist_mac_os_not_supported(self, mock_host_distname,
                                                    mock__get_disturl,
                                                    mock__get_pkgname,
                                                    mock_system):
        mock__get_pkgname.return_value = "radare2-5.3.1-mac.zip"
        mock__get_disturl.return_value = "http://example.org"
        mock_host_distname.return_value = "not_existing_so"
        patch("r2env.package_manager.wget.download").start()
        with self.assertRaises(PackageManagerException):
            self.package_manager._install_from_dist("radare2", "5.6.0")
        mock_system.assert_not_called()

    @patch("r2env.package_manager.PackageManager._uninstall_from_dist")
    @patch("r2env.package_manager.zipfile.ZipFile")
    def test_install_windows_package_file_not_found(self, zipfile_mock, uninstall_mock):
        zipfile_mock.extractall.side_effect = FileNotFoundError()
        with self.assertRaises(PackageManagerException):
            self.package_manager._install_windows_package("radare2")
        uninstall_mock.assert_called_once()

    @patch("r2env.package_manager.os.path.isdir")
    @patch("r2env.package_manager.os.makedirs")
    def test_install_windows_package_create_dst_folder(self, makedirs_mock, isdir_mock):
        patch("r2env.package_manager.shutil.copyfile").start()
        patch("r2env.package_manager.zipfile").start()
        isdir_mock.return_value = False
        patch("r2env.package_manager.shutil.copyfile").start()
        self.package_manager._install_windows_package("radare2")
        makedirs_mock.assert_called_once_with(os.path.join(self.package_manager._r2env_path, "bin"), 493)

    @patch("r2env.package_manager.os.path.isdir")
    def test_install_windows_package_successfully(self, isdir_mock):
        with patch("r2env.package_manager.zipfile.ZipFile") as mock_ZipFile:
            mock_zip = MagicMock()
            mock_zip.return_value = ["1", "2", "3"]
            mock_ZipFile.return_value = mock_zip
            mock_copy = patch("r2env.package_manager.shutil.copyfile").start()
            isdir_mock.return_value = True
            assert_that(self.package_manager._install_windows_package("radare2"), equal_to(True))
            mock_copy.assert_called_once()

    @patch("r2env.package_manager.host_distname")
    def test_uninstall_from_dist_windows(self, mock_distname):
        mock_distname.return_value = "w64"
        mock_rmtree = patch("r2env.package_manager.shutil.rmtree").start()
        dst_folder = os.path.join(self.package_manager._r2env_path, "bin")
        assert_that(self.package_manager._uninstall_from_dist("radare2", "1.0.0"), equal_to(True))
        mock_rmtree.assert_called_once_with(dst_folder)

    @patch("r2env.package_manager.host_distname")
    def test_uninstall_from_dist_mac(self, mock_distname):
        mock_distname.return_value = "mac_arm64"
        mock_system = patch("r2env.package_manager.os.system").start()
        mock_system.side_effect = [0,0,0,0]
        assert_that(self.package_manager._uninstall_from_dist("radare2", "1.0.0"), equal_to(True))

    @patch("r2env.package_manager.host_distname")
    def test_uninstall_from_dist_mac_failed(self, mock_distname):
        mock_distname.return_value = "mac_arm64"
        mock_system = patch("r2env.package_manager.os.system").start()
        mock_system.side_effect = [0,1,0,0]
        assert_that(self.package_manager._uninstall_from_dist("radare2", "1.0.0"), equal_to(False))

    @patch("r2env.package_manager.host_distname")
    def test_uninstall_from_dist_linux(self, mock_distname):
        mock_distname.return_value = "deb_x64"
        mock_system = patch("r2env.package_manager.os.system").start()
        mock_system.return_value = 0
        assert_that(self.package_manager._uninstall_from_dist("radare2", "1.0.0"), equal_to(True))
        mock_system.assert_called_once_with("sudo dpkg -r radare2")

    @patch("r2env.package_manager.host_distname")
    def test_uninstall_from_dist_os_not_supported(self, mock_distname):
        mock_distname.return_value = "non_existent"
        with self.assertRaises(PackageManagerException):
            self.package_manager._uninstall_from_dist("radare2", "1.0.0")

    @patch("r2env.package_manager.host_distname")
    def test_acr_not_supported_on_windows(self, mock_distname):
        mock_distname.return_value = "w64"
        with self.assertRaises(PackageManagerException):
            self.package_manager._build_using_acr("source", "dest", "logfile", "r2env")
