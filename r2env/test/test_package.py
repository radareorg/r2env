import os

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
