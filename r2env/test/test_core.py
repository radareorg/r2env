from doublex import assert_that
from hamcrest import equal_to
from mock import patch
import unittest

from r2env.core import R2Env
from r2env.exceptions import R2EnvException


class TestCore(unittest.TestCase):
    def setUp(self):
        self.packages_dir = ["5.3.0"]

        self.profiles = {
                            "radare2": {
                            "source": "https://github.com/radareorg/radare2",
                            "versions": [
                              {
                                "id": "5.3.0",
                                "packages": {
                                  "w64": "radare2-5.3.0-w64.zip",
                                  "deb_x64": "radare2_5.3.0_amd64.deb"
                                }
                              }
                            ]
                            }
                        }


    def tearDown(self):
        patch.stopall()

    @patch("r2env.core.R2Env._get_default_path")
    def test_default_config(self, mock_default_path):
        _ = R2Env()
        mock_default_path.assert_called()

    @patch("r2env.core.load_json_file")
    def test_custom_config_using_json_file(self, mock_load_json_file):
        custom_r2_path = "custom_r2_path"
        mock_load_json_file.return_value = {"r2env_path": "custom_r2_path"}
        r2env = R2Env()
        assert_that(r2env._r2env_path, equal_to(custom_r2_path))

    @patch("os.getenv")
    def test_custom_config_using_envvar(self, mock_getenv):
        custom_r2_path = "custom_r2_path"
        mock_getenv.return_value = custom_r2_path
        r2env = R2Env()
        assert_that(r2env._r2env_path, equal_to(custom_r2_path))

    @patch("os.mkdir")
    @patch("os.path.isdir")
    def test_init_failed(self, mock_isdir, mock_mkdir):
        mock_isdir.return_value = True
        R2Env().init()
        mock_mkdir.assert_not_called()

    @patch("os.mkdir")
    @patch("os.path.isdir")
    def test_init_successfully(self, mock_isdir, mock_mkdir):
        mock_isdir.return_value = False
        r2env= R2Env()
        r2env.init()
        mock_mkdir.assert_called_with(r2env._r2env_path)

    @patch("os.path.isdir")
    def test_check_if_r2env_not_initialized(self, mock_isdir):
        mock_isdir.return_value = False
        with self.assertRaises(R2EnvException):
            R2Env().check_if_r2env_initialized()

    @patch("r2env.core.print_console")
    @patch("r2env.core.PackageManager.list_available_packages")
    def test_list_available_pkg_successfully(self, mock_list_pkg, mock_print_console):
        mock_list_pkg.return_value = self.profiles
        R2Env().list_available_packages()
        mock_print_console.assert_called_with(" - radare2@5.3.0  - w64, deb_x64", formatter=1)

    @patch("r2env.core.R2Env._get_current_version")
    @patch("r2env.core.print_console")
    @patch("os.path.isdir")
    @patch("r2env.core.PackageManager.list_installed_packages")
    def test_list_installed_pkg_successfully(self, mock_list_pkg, mock_isdir, mock_print, mock_current):
        mock_list_pkg.return_value = self.packages_dir
        mock_isdir.return_value = True
        R2Env().list_installed_packages()
        mock_print.assert_called_with("  - 5.3.0")
        mock_current.return_value = "5.3.0"
        R2Env().list_installed_packages()
        mock_print.assert_called_with("  - 5.3.0 (in use)")

    def test_check_package_format(self):
        r2env = R2Env()
        assert_that(r2env._check_package_format("radare2@git"), equal_to(True))
        assert_that(r2env._check_package_format("radare2@5.3.0"), equal_to(True))
        assert_that(r2env._check_package_format("radare2@5.30"), equal_to(False))
        assert_that(r2env._check_package_format("1234@5.30"), equal_to(False))
        assert_that(r2env._check_package_format("radare2git"), equal_to(False))

    @patch("r2env.core.R2Env._check_package_format")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    @patch("r2env.core.PackageManager.install_package")
    def test_install_successfully_default(self, mock_pkg_install, mock_initialized, mock_valid_format):
        mock_initialized.return_value = True
        mock_valid_format.return_value = True
        package = "radare2"
        version = "5.3.0"
        R2Env().install(f"{package}@{version}")
        mock_pkg_install.assert_called_with(package, version, use_meson=False, use_dist=False)

    @patch("r2env.core.R2Env._check_package_format")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    @patch("r2env.core.PackageManager.install_package")
    def test_install_successfully_meson(self, mock_pkg_install, mock_initialized, mock_valid_format):
        mock_initialized.return_value = True
        mock_valid_format.return_value = True
        package = "radare2"
        version = "5.3.0"
        R2Env().install(f"{package}@{version}", use_meson=True)
        mock_pkg_install.assert_called_with(package, version, use_meson=True, use_dist=False)

    @patch("r2env.core.R2Env._check_package_format")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    @patch("r2env.core.PackageManager.install_package")
    def test_install_successfully_dist(self, mock_pkg_install, mock_initialized, mock_valid_format):
        mock_initialized.return_value = True
        mock_valid_format.return_value = True
        package = "radare2"
        version = "5.3.0"
        R2Env().install(f"{package}@{version}", use_dist=True)
        mock_pkg_install.assert_called_with(package, version, use_meson=False, use_dist=True)

    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    def test_install_successfully_failed(self, mock_initialized):
        mock_initialized.return_value = True
        package = "radare2@"
        version = ""
        with self.assertRaises(R2EnvException):
            R2Env().install(f"{package}{version}", use_dist=True)

    @patch("r2env.core.R2Env._check_package_format")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    @patch("r2env.core.PackageManager.install_package")
    def test_install_successfully_failed_with_default(self, mock_pkg_install, mock_initialized, mock_valid_format):
        mock_initialized.return_value = True
        mock_valid_format.return_value = True
        package = "radare2"
        R2Env().install(package)
        mock_pkg_install.assert_called_with(package, "git", use_meson=False, use_dist=False)

    @patch("r2env.core.R2Env._check_package_format")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    @patch("r2env.core.PackageManager.uninstall_package")
    def test_uninstall_successfully_default(self, mock_pkg_uninstall, mock_initialized, mock_valid_format):
        mock_initialized.return_value = True
        mock_valid_format.return_value = True
        package = "radare2@5.3.0"
        R2Env().uninstall(package)
        mock_pkg_uninstall.assert_called_with(package, False)

    @patch("r2env.core.R2Env._check_package_format")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    @patch("r2env.core.PackageManager.uninstall_package")
    def test_uninstall_successfully_dist(self, mock_pkg_uninstall, mock_initialized, mock_valid_format):
        mock_initialized.return_value = True
        mock_valid_format.return_value = True
        package = "radare2@5.3.0"
        R2Env().uninstall(package, use_dist=True)
        mock_pkg_uninstall.assert_called_with(package, True)

    @patch("r2env.core.R2Env._check_package_format")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    def test_uninstall_failed(self, mock_initialized, mock_valid_format):
        mock_initialized.return_value = True
        mock_valid_format.return_value = False
        package = "radare2@5.3.0"
        with self.assertRaises(R2EnvException):
            R2Env().uninstall(package, use_dist=True)

    @patch("shutil.rmtree")
    def test_purge(self, mock_rmtree):
        r2env = R2Env()
        r2env.purge()
        mock_rmtree.assert_called_with(r2env._r2env_path)


    @patch("r2env.core.PackageManager.list_installed_packages")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    def test_use_package_not_installed(self, mock_initialized, mock_list_pkg):
        package = "radare2@not_existing"
        mock_list_pkg.return_value = ["radare2@1.0.0"]
        mock_initialized.return_value = True
        r2env = R2Env()
        with self.assertRaises(R2EnvException):
            r2env.use(package)

    @patch("r2env.core.PackageManager.list_installed_packages")
    @patch("r2env.core.PackageManager.get_package_path")
    @patch("r2env.core.unstow")
    @patch("r2env.core.stow")
    @patch("r2env.core.R2Env._set_current_version")
    @patch("r2env.core.R2Env._get_current_version")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    def test_use_successfully(self, mock_initialized, mock_get_cur_ver, mock_set_cur_ver, mock_stow, mock_unstow,
                              mock_pkg_path, mock_list_pkg):
        package = "radare2@5.3.0"
        mock_initialized.return_value = True
        mock_get_cur_ver.return_value = "5.3.0"
        mock_list_pkg.return_value = ["radare2@5.3.0"]
        new_path = f"new_path/{package}"
        curr_path = f"new_path/old_package"
        mock_pkg_path.side_effect = [new_path, curr_path]
        r2env = R2Env()
        r2env.use(package)
        mock_set_cur_ver.assert_called_once_with(package)
        mock_stow.assert_called_once_with([new_path], r2env._r2env_path)
        mock_unstow.assert_called_once_with([curr_path], r2env._r2env_path)

    @patch("r2env.core.PackageManager.list_installed_packages")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    def test_use_with_no_none_package(self, mock_initialized, mock_list_pkg):
        mock_initialized.return_value = True
        r2env = R2Env()
        with self.assertRaises(R2EnvException):
            r2env.use(None)
        mock_list_pkg.assert_called_once()

    @patch("r2env.core.PackageManager.list_installed_packages")
    @patch("r2env.core.R2Env.check_if_r2env_initialized")
    def test_use_with_no_package(self, mock_initialized, mock_list_pkg):
        mock_initialized.return_value = True
        r2env = R2Env()
        with self.assertRaises(R2EnvException):
            r2env.use()
        mock_list_pkg.assert_called_once()


    @patch("r2env.core.PackageManager")
    @patch("r2env.core.os.path.join")
    @patch("r2env.core.host_platform")
    @patch("r2env.core.os.system")
    @patch("r2env.core.load_json_file")
    def test_shell_windows(self, mock_load_json_file, mock_system, mock_host_platform, mock_join, _):
        def side_effect(path1, path2, *args):
            return f"{path1}\\{path2}"
        r2env_path = "c:\\windows\\temp\\r2env\\"
        mock_join.side_effect = side_effect
        mock_host_platform.return_value = "windows"
        mock_load_json_file.return_value = {"r2env_path": r2env_path}
        cmd = "r2 -v"
        R2Env().shell(cmd)
        mock_system.assert_called_with(f"set PATH={r2env_path}\\bin;%PATH% && cmd")

    @patch("r2env.core.host_platform")
    @patch("r2env.core.os.system")
    @patch("r2env.core.load_json_file")
    def test_shell_android(self, mock_load_json_file, mock_system, mock_host_platform):
        mock_host_platform.return_value = "android"
        r2env_path = "/tmp/r2env"
        mock_load_json_file.return_value = {"r2env_path": r2env_path}
        cmd = "r2 -v"
        R2Env().shell(cmd)
        mock_system.assert_called_with(f"export LD_LIBRARY_PATH=\"{r2env_path}/lib\";"
                                       f"export PS1=\"r2env ()\\$ \";"
                                       f"export PKG_CONFIG_PATH=\"{r2env_path}/lib/pkgconfig\";"
                                       f"export PATH=\"{r2env_path}/bin:$PATH\";"
                                       f"$SHELL -f -c \'{cmd}\'")

    @patch("r2env.core.host_platform")
    @patch("r2env.core.os.system")
    @patch("r2env.core.load_json_file")
    def test_shell_osx(self, mock_load_json_file, mock_system, mock_host_platform):
        mock_host_platform.return_value = "osx"
        r2env_path = "/tmp/r2env"
        mock_load_json_file.return_value = {"r2env_path": r2env_path}
        cmd = "r2 -v"
        R2Env().shell(cmd)
        mock_system.assert_called_with(f"export DYLD_LIBRARY_PATH=\"{r2env_path}/lib\";"
                                       f"export PS1=\"r2env ()\\$ \";"
                                       f"export PKG_CONFIG_PATH=\"{r2env_path}/lib/pkgconfig\";"
                                       f"export PATH=\"{r2env_path}/bin:$PATH\";"
                                       f"$SHELL -f -c \'{cmd}\'")

    @patch("r2env.core.host_platform")
    @patch("r2env.core.os.system")
    @patch("r2env.core.load_json_file")
    def test_shell_linux(self, mock_load_json_file, mock_system, mock_host_platform):
        mock_host_platform.return_value = "linux"
        r2env_path = "/tmp/r2env"
        mock_load_json_file.return_value = {"r2env_path": r2env_path}
        cmd = "r2 -v"
        R2Env().shell(cmd)
        mock_system.assert_called_with(f"export PS1=\"r2env ()\\$ \";"
                                       f"export PKG_CONFIG_PATH=\"{r2env_path}/lib/pkgconfig\";"
                                       f"export PATH=\"{r2env_path}/bin:$PATH\";"
                                       f"$SHELL -f -c \'{cmd}\'")
