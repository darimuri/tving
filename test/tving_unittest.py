# -*- coding: utf-8 -*-
import unittest   # The test framework
import os
import sys
import auth
import api

class Test_TestIncrementDecrement(unittest.TestCase):
    api = None
    def setUp(self):
        self.api = api.TvingAPI("login.dat", "programlist.txt")
        isLogin, e = self.api.DoLogin(auth.id, auth.password, "CJONE")
        self.assertTrue(isLogin)
        self.assertEqual(e, "Log")

    def test_GetLoginData2(self):
        loginData = self.api.GetLoginData2(auth.id, auth.password, "CJONE")
        self.assertIsNotNone(loginData)
        self.assertIsNotNone(loginData['t'])
        self.assertTrue(loginData['t'].startswith("_tving_token="))

    def test_GetList(self):
        param = None
        hasMore, listData = self.api.GetList('LIVE', param, 1)
        self.assertEqual(hasMore, 'Y', "hasMore should be Y")
        self.assertIsNotNone(listData)

        ret = self.api.GetURL(listData[0]['live_code'], api.QUALITYS['HD'], auth.id, auth.password, "CJONE")
        self.assertIsNotNone(ret)

if __name__ == '__main__':
    unittest.main()
