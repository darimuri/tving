# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import os
import json
import re
import pickle
import ssl
from io import open


class TvingAPI:
    loginDataPath = ""
    sjvaUrl = ""
    sjvaToken = ""

    def __init__(self, loginDataPath, sjvaUrl, sjvaToken):
        self.loginDataPath = loginDataPath
        self.sjvaUrl = sjvaUrl
        self.sjvaToken = sjvaToken

    def GetBroadURL(self, code, quality, id, pw, login_type):
        try:
            login = GetLoginData()
            if len(login) == 0:
                login = self.GetLoginData2(id, pw, login_type)
            login2 = login['t'].split(
                '=')[1] if login is not None and 't' in login else ''
            url = self.sjvaUrl + '/tving/api/decrypt?sjva_token=%s&c=%s&q=%s&t=%s' % (
                self.sjvaToken, code, quality, login2)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            urllib2.install_opener(opener)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            ret = response.read().strip()
            return ret
        except Exception as e:
            raise e
        return

    def GetLoginData(self):
        try:
            file = open(self.loginDataPath, 'rb')
            login = pickle.load(file)
            file.close()
        except Exception, e:
            raise e
            login = []
        return login

    def GetLoginData2(self, user_id, user_pw, type):
        isLogin = False
        try:
            loginData = {}
            url = 'https://user.tving.com/user/doLogin.tving'
            if type == 'CJONE':
                loginType = '10'
            else:
                loginType = '20'
            params = {'userId': user_id,
                      'password': user_pw,
                      'loginType': loginType}

            postdata = urllib.urlencode(params)
            request = urllib2.Request(url, postdata)
            response = urllib2.urlopen(
                request, context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
            cookie = response.info().getheader('Set-Cookie')
            for c in cookie.split(','):
                c = c.strip()
                if c.startswith('cs'):
                    loginData['p'] = c.split('=')[1].split(
                        ';')[0].replace('%3D', '=').replace('%3B', '&')
                if c.startswith('_tving_token'):
                    loginData['t'] = c.split(';')[0]
            return loginData
        except Exception as e:
            raise e
            credential = 'none'
        return []
