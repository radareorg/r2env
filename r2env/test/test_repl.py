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
        no_action = ""
        with self.assertRaises(ActionException):
            self.repl.run_action(no_action)
