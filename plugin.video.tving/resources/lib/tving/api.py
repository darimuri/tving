# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import os
import time
import json
import re
import base64
import pickle
import ssl
from io import open

DEFAULT_PARAM = '&screenCode=CSSD0100&networkCode=CSND0900&osCode=CSOD0900&teleCode=CSCD0900&apiKey=1e7952d0917d6aab1f0293a063697610'
QUALITYS = {'FHD':'stream50', 'HD':'stream40', 'SD':'stream30'}
QUALITYS_STRING = ['FHD', 'HD', 'SD']
MENU_LIST = [
    'LIVE:인기 LIVE:',
    'LIVE:TV 채널:&channelType=CPCS0100',
    'LIVE:TVING TV:&channelType=CPCS0300',
    'VOD::&free=all&lastFrequency=y', 
    'VOD:무료 :&free=y&multiCategoryCode=PCA%2CPCD%2CPCG%2CPCZ%2CPCN%2CPCF%2CPCC%2CPCAN%2CPCE%2CPCI%2CPCJ%2CPCK%2CPCH%2CPCPOS&lastFrequency=y',
    'VOD:드라마 :&free=all&multiCategoryCode=PCA&lastFrequency=y',
    'VOD:예능/뮤직 :&free=all&multiCategoryCode=PCD%2CPCG%2CPCZ&lastFrequency=y',
    'VOD:스타일/푸드 :&free=all&multiCategoryCode=PCN%2CPCF&lastFrequency=y',
    'VOD:키즈/애니메이션 :&free=all&multiCategoryCode=PCC%2CPCAN&lastFrequency=y',
    'VOD:e스포츠 :&free=all&multiCategoryCode=PCE&lastFrequency=y',
    'VOD:교양 :&free=all&multiCategoryCode=PCI%2CPCJ%2CPCK%2CPCH&lastFrequency=y',
    'VOD:해외TV :&free=all&multiCategoryCode=PCPOS&lastFrequency=y',
    'VOD:웹드라마 :&free=all&multiCategoryCode=PCWD&lastFrequency=y']
VOD_GENRE = ['최신:&order=broadDate', '인기:&order=viewDay']

VERSION = '0.4.0'

class TvingAPI:
    loginDataPath = ""
    programListPath = ""

    def __init__(self, loginDataPath, programListPath, sjvaUrl, sjvaToken):
        self.loginDataPath = loginDataPath

    def GetBroadURL(self, code, quality, id, pw, login_type):
        login = self.GetLoginData()
        if len(login) == 0:
            login = self.GetLoginData2(id, pw, login_type)
        token = login['t'].split(
            '=')[1] if login is not None and 't' in login else ''
        return self.get_episode_json_default(code, quality, token)

    def GetURL(self, code, quality, id, pw, login_type):
        return self.GetBroadURL(code, quality, id, pw, login_type)

    def LoadWatchedList(self):
        try:
            f = open(self.programListPath, 'r', encoding='utf-8')
            result = f.readlines()
            f.close()
            return result
        except Exception as e:
            raise e
        return result

    def SaveWatchedList(self, data):
        try:
            result = self.LoadWatchedList()
            with open(self.programListPath, 'w', encoding='utf-8') as fw:
                #data = unicode(data + '\n')
                data = (data + '\n').decode('utf8')
                fw.write(data)
                num = 1
                for line in result:
                    if line.find(data.split('|')[1]) == -1: 
                        fw.write(line)
                        num += 1
                    if num == 100: break
        except Exception as e:
            raise e
        return

    def GetMenu(self):
        list = []
        for item in MENU_LIST:
            if item.startswith('LIVE'): list.append(item)
            else:
                tmp = item.split(':')
                list.append(tmp[0]+':'+tmp[1]+VOD_GENRE[0].split(':')[0]+':'+tmp[2]+VOD_GENRE[0].split(':')[1])
                list.append(tmp[0]+':'+tmp[1]+VOD_GENRE[1].split(':')[0]+':'+tmp[2]+VOD_GENRE[1].split(':')[1])
        return list

    def DoStartLoginCheck(self, id, pw, login_type, use_local_logindata):
        if id == '' : id = None
        if pw == '' : pw = None
        message = '['
        if id is None or pw is None:
            message += '아이디/암호 정보가 없습니다.'
        else:
            status = self.GetLoginStatus()
            if status == 'NOT_LOGIN_FILE' or status == 'LOGIN_FAIL' or use_local_logindata == False or use_local_logindata == 'false':
                self.DoLogin(id, pw, login_type)
                status = self.GetLoginStatus()
                if status == 'SUCCESS': 
                    message += '로그인 정보를 저장했습니다. '
                    if str(use_local_logindata): message += '저장된 정보로 로그인합니다.'
                    else: message += '매번 로그인합니다.'
                elif status == 'LOGIN_FAIL': message += '로그인에 실패하였습니다.'
            elif status == 'SUCCESS': message += '저장된 로그인 정보가 있습니다.' 
            elif status == 'LOGIN_FAIL': message += '로그인 파일은 있으나 유효하지 않습니다'
        message += ']'
        return message


    def GetLoginStatus(self):
        if os.path.isfile(self.loginDataPath):
            login_data = self.GetLoginData()
            if 't' in login_data: return 'SUCCESS'
            else: return 'LOGIN_FAIL'
        else:
            return 'NOT_LOGIN_FILE'

    def GetLoginData(self):
        try:
            file = open(self.loginDataPath, 'rb')
            login = pickle.load(file)
            file.close()
        except Exception, e:
            raise e
        return login

    def GetLoginData2(self, user_id, user_pw, type):
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
        return []

    def DoLogin(self, user_id, user_pw, type ):
        e = 'Log'
        isLogin = False
        try:
            if os.path.isfile(self.loginDataPath): os.remove(self.loginDataPath)
            loginData = {}
            url = 'https://user.tving.com/user/doLogin.tving'
            if type == 'CJONE': loginType = '10'
            else: loginType = '20'
            params = { 'userId' : user_id,
                'password' : user_pw,
                'loginType' : loginType }
            
            postdata = urllib.urlencode( params )
            request = urllib2.Request(url, postdata)
            response = urllib2.urlopen(request, context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
            cookie = response.info().getheader('Set-Cookie')
            for c in cookie.split(','):
                c = c.strip()
                if c.startswith('cs'): 
                    loginData['p'] = c.split('=')[1].split(';')[0].replace('%3D', '=').replace('%3B', '&')
                if c.startswith('_tving_token'):
                    loginData['t'] = c.split(';')[0]
                
            file = open(self.loginDataPath, 'wb')
            pickle.dump(loginData, file)
            file.close()
            isLogin = True
        except Exception as e:
            raise e
        return (isLogin, e)

    def GetList(self, type, param, page):
        has_more = 'N'
        try:
            result = []
            if type == 'WATCHED':
                for line in self.LoadWatchedList():
                    info = {}
                    tmp = line.strip().split('|')
                    info['type'] = tmp[0]
                    info['code'] = tmp[1]
                    info['title'] = tmp[2]
                    info['img'] = tmp[3]
                    result.append(info)
                return 'N', result

            if type == 'LIVE': url = 'http://api.tving.com/v1/media/lives?pageNo=%s&pageSize=20&order=rating&adult=all&free=all&guest=all&scope=all' % page
            else: url = 'http://api.tving.com/v1/media/episodes?pageNo=%s&pageSize=18&adult=all&guest=all&scope=all&personal=N' % page
            if param is not None: url += param
            url += DEFAULT_PARAM			

            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            data = json.load(response, encoding="utf-8")
            
            for item in data["body"]["result"]:
                try:
                    info = {}
                    if type == 'LIVE':
                        info['live_code'] = item["live_code"]
                        info['channel_title'] = item['schedule']['channel']['name']['ko']
                        info['episode_title'] = ' '
                        info['img'] = 'http://image.tving.com/upload/cms/caic/CAIC1900/%s.png' % item["live_code"]
                        if item['schedule']['episode'] is not None:
                            info['episode_title'] = item['schedule']['episode']['name']['ko']
                            if info['channel_title'].startswith('CH.') and len(item['schedule']['episode']['image']) > 0:
                                info['img'] = 'http://image.tving.com' + item['schedule']['episode']['image'][0]['url']
                        info['free'] = (item['schedule']['broadcast_url'][0]['broad_url1'].find('drm') == -1)
                    else:
                        info['program_code'] = item["program"]["code"]
                        info['program_title'] = item["program"]["name"]["ko"]
                        info['program_summary'] = item["program"]["synopsis"]["ko"]
                        info['program_image'] = "http://image.tving.com" + item["program"]["image"][0]["url"]
                        info['episode_code'] = item["episode"]["code"]
                        info['episode_title'] = item["episode"]["name"]["ko"]
                        info['episode_summary'] = item["episode"]["synopsis"]["ko"]
                        info['episode_image'] = "http://image.tving.com" + item["episode"]["image"][0]["url"]
                        info['stream'] = item["stream_support_info"]
                        info['free'] = item["episode"]["free_yn"]
                    result.append(info)
                except:
                    pass
            has_more = data["body"]["has_more"]
        except Exception as e:
            raise e
        return has_more, result

    def get_episode_json_default(self, episode_code, quality, token):
        ts = '%d' % time.time()

        try:
            url = 'http://api.tving.com/v1/media/stream/info?info=y%s&noCache=%s&mediaCode=%s&streamCode=%s&callingFrom=FLASH' % (DEFAULT_PARAM, ts, episode_code, quality)
            request = urllib2.Request(url)
            request.add_header('Cookie', token)
            response = urllib2.urlopen(request)
            data = json.load(response)
            url = data['body']['stream']['broadcast']['broad_url']
            decrypted_url = self.decrypt(episode_code, ts, url)
            if decrypted_url.find('m3u8') == -1:
                decrypted_url = decrypted_url.replace('rtmp', 'http')
                decrypted_url = decrypted_url.replace('?', '/playlist.m3u8?')
            return decrypted_url
        except Exception as e:
            raise e

        return

    def decrypt(self, code, key, value):
        try:
            from Crypto.Cipher import DES3
            cryptoCode = 'cjhv*tving**good/%s/%s' % (code[-3:], key)
            key = cryptoCode[:24]
            data = base64.decodestring(value)
            iv = '\x00\x00\x00\x00\x00\x00\x00\x00'
            des3 = DES3.new(key, DES3.MODE_ECB)
            ret = des3.decrypt(data)
            pad_len = ord(ret[(-1)])
            ret = ret[:-pad_len]
            return ret
        except Exception as e:
            raise e
