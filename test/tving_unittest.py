# -*- coding: utf-8 -*-
import unittest   # The test framework
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "../plugin.video.tving", 'resources', 'lib'))
from tving import *


class Test_TestIncrementDecrement(unittest.TestCase):
    def setUp(self):
        self.api = TvingAPI("login.dat", "http://192.168.0.100:9999", "abcde")

    def test_increment(self):
        self.assertEqual(4, 4)

    def test_decrement(self):
        self.assertEqual(4, 4)


if __name__ == '__main__':
    unittest.main()
