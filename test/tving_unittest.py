# -*- coding: utf-8 -*-
import unittest   # The test framework
import os
import sys
from tving import api

class Test_TestIncrementDecrement(unittest.TestCase):
    api = None
    def setUp(self):
        self.api = api.TvingAPI("login.dat", "programlist.txt", "http://192.168.0.100:9999", "abcde")
        isLogin, e = self.api.DoLogin("dormael", "dkanskrn12#", "CJONE")
        self.assertTrue(isLogin)
        self.assertEqual(e, "Log")

    def test_GetLoginData2(self):
        loginData = self.api.GetLoginData2("dormael", "dkanskrn12#", "CJONE")
        self.assertIsNotNone(loginData)
        self.assertIsNotNone(loginData['t'])
        self.assertTrue(loginData['t'].startswith("_tving_token="))

if __name__ == '__main__':
    unittest.main()
