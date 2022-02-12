from mock import patch
import unittest

from r2env.repl import REPL
from r2env.exceptions import ActionException


class MockActions:
    def __init__(self):
        self.args = []
        self.version = False
        self.list = False


class TestRepl(unittest.TestCase):
    def setUp(self):
        self.repl = REPL()

    def tearDown(self):
        patch.stopall()
    
    def test_invalid_run_with_no_action(self):
        with self.assertRaises(ActionException):
            self.repl.run_action(None)
        no_action = MockActions()
        with self.assertRaises(ActionException):
            self.repl.run_action(no_action)

    @patch("r2env.repl.R2Env.list_packages")
    @patch("r2env.repl.R2Env.list_installed_packages")
    def test_invalid_run_action_with_no_arguments(self,mock_list_installed_packages, mock_list_packages):
        use_action = MockActions()
        use_action.args.append("use")
        with self.assertRaises(ActionException):
            self.repl.run_action(use_action)
        mock_list_installed_packages.assert_called()
        install_action = MockActions()
        install_action.args.append("install")
        with self.assertRaises(ActionException):
            self.repl.run_action(install_action)
        mock_list_packages.assert_called()

    @patch("r2env.repl.REPL.show_help")
    def test_print_help(self, mock_help):
        help_action = MockActions()
        with self.assertRaises(ActionException):
            self.repl.run_action(help_action)
        mock_help.assert_called()

    def test_invalid_action(self):
        invalid_action = MockActions()
        invalid_action.args.append("invalid_action")
        with self.assertRaises(ActionException):
            self.repl.run_action(invalid_action)

