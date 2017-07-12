#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json,os,sys
import http.cookiejar
import requests
from html.parser import HTMLParser
from urllib import parse
class titleparser(HTMLParser):
    count,title_dict=1,{}
    def title_clear(self):
        self.count,self.title_dict=1,{}
    def feedupdate(self,func):#用于feed方法重置count和title_dict的值
        def wrapper(*args,**kw):
            self.count,self.title_dict=1,{}
            #print('title dicts reset')
            return func(*args,**kw)
        return wrapper
    def handle_starttag(self,tag,attrs):
        if tag == 'a':
            for name,value in attrs:
                if name == 'class':#class="card_title_fname"为贴吧名称
                    if value == ' card_title_fname':
                        for name,value in attrs:
                            if name == 'href':
                                #print('贴吧名称：%s'%(parse.unquote(value)))
                                self.title_dict['name']=parse.unquote(value)
                    if value == 'j_th_tit ':#class="j_th_tit"为主题贴
                        #print('%d.%s=%s;%s=%s'%(self.count,attrs[0][0],attrs[0][1],attrs[1][0],attrs[1][1]))
                        self.title_dict[str(self.count)]=(attrs[0][1][3:13],attrs[1][1])
                        self.count+=1
class subjectparser(HTMLParser):
    def handle_starttag(self,tag,attrs):
        if tag == 'div':
            pass
class BaiduTieba(object):
    LOGIN_ERR_MSGS = {
    "1": "用户名格式错误，请重新输入",
    "2": "用户不存在",
    "3": "",
    "4": "登录密码错误，请重新输入",
    "5": "今日登陆次数过多",
    "6": "验证码不匹配，请重新输入验证码",
    "7": "登录时发生未知错误，请重新输入",
    "8": "登录时发生未知错误，请重新输入",
    "16": "对不起，您现在无法登陆",
    "51": "改手机号未通过验证",
    "52": "该手机已经绑定多个用户",
    "53": "手机号码格式不正确",
    "58": "手机号格式错误，请重新输入",
    "256": "",
    "257": "请输入验证码",
    "20": "此账号已登录人数过多",
    "default": "登录时发生未知错误，请重新输入"
    }
    POST_ERR_MSGS = {
    "38": "验证码超时，请重新输入",
    "40": "验证码输入错误，请您返回后重新输入",
    "703": "为了减少恶意灌水和广告贴，本吧被设置为仅本吧会员才能发帖",
    "704": "为了减少恶意灌水和广告贴，本吧被设置为仅本吧管理团队才能发帖，给您带来的不便表歉意",
    "705": "本吧当前只能浏览，不能发帖！",
    "706": "抱歉，本帖暂时无法回复。",
    "900": "为抵御挖坟威海，本吧吧主已放出贴吧神兽--超级静止蛙，本帖暂时无法回复。",
    }
    CookiePath=os.path.expanduser('~')+'/baidu-cookies'
    Referer='https://tieba.baidu.com'
    LOGIN_URL="http://passport.baidu.com/?login"
    USER_INFO="http://tieba.baidu.com/f/user/json_userinfo"
    LOGIN_IMG_URL="http://passport.baidu.com/?verifypic"
    POST_URL="http//tieba.baidu.com/f/commit/thread/add"
    THREAD_URL="http://tieba.baidu.com/f/commit.thread/add"
    TBS_URL="http://tieba.baidu.com/dc/common/tbs"
    VCODE_URL="http://tieba.baidu.com/f/user/json_vocde? lm=%s&rs10=2&rs1=0&t=0.7"
    IMG_URL="http://tieba.baidu.com/cgi-bin/genimg?%s"
    try:
        with open('title_dict.log','r') as fp:
            title_dict=json.load(fp)
    except:
        pass
    def __init__(self,user=None,passwd=None):
        self.user=user
        self.passwd=passwd
        self.cj=self._CookieTest()
        self._LoginTest()
    def _LoginTest(self,user=None,passwd=None):
        if self.cj:#检测到有效cookies时使用cookies登录
            req=self.Session().get(self.USER_INFO)
            js=json.loads(req.text)
            if js['data']['is_login'] == True:
                print("使用cookies登陆成功!\nHello %s welcome to back tieba!"%js['data']['user_name_show'])
            else:
                print("cookies登陆失败")
        else:
            pass
    def _title_print(self):
        print('贴吧名称: %s'%self.title_dict['name'])
        for i in range(len(self.title_dict)-1):#title_dict长度，去掉name
            print('%d.href=/p%s;title=%s'%(i+1,self.title_dict[str(i+1)][0],self.title_dict[str(i+1)][1]))
    def _CookieTest(self):
        try:
            cj=http.cookiejar.MozillaCookieJar(self.CookiePath+'/mozilla-cookies.txt')
            cj.load()
            print('cookies loading correctly')
            return cj
        except:
            print('cookie file seems discorrect,you can make a new cookies file \nfrom firefox firebug and save to your ${HOME}/baidu-cookies')
            self.mozilla_cookies_resave()
    def user_agent(self,agent):
        with open('user-agent.json') as fp:
            return json.load(fp)[agent]
    def Mozilla_Firebug_cookies_checker(self,path='/cookies.txt'):
        '''将firebug模式的cookies.txt转换为标准格式的MozillaCookieJar'''
        cookie='# Netscape HTTP Cookie File\n'
        with open(self.CookiePath+path,'r') as fp:
            for line in fp.readlines():
                if line.split('\t')[4].isnumeric():
                    cookie+=line
        return cookie
    def mozilla_cookies_resave(self):
        '''重新生成一个cookies文件'''
        try:
            with open(self.CookiePath+'/mozilla-cookies.txt','w') as fp:
                fp.write(self.Mozilla_Firebug_cookies_checker())
                print('Mozilla cookies saved!')
        except:
            print('cookies file discorrect!')
    def Session(self,agent="Ie"):
        S=requests.Session()
        if self.cj :
            S.cookies.update(self.cj)
        S.headers.update({'User-Agent':self.user_agent(agent)})
        return S
    def TiebaList(self,tieba_name,agent="Ie"):
        url='https://tieba.baidu.com/f?kw=%s&fr=index'%tieba_name
        self.title_dict={}
        req=self.Session(agent).get(url)
        P=titleparser()
        P.feed=P.feedupdate(P.feed)#feed方法装饰升级
        P.feed(req.text)
        self.title_dict=P.title_dict
        self._title_print()
        with open('title_dict.log','w') as fp:
            fp.write(json.dumps(P.title_dict))
        return req
    def SubjectReader(self,title_index,page_number=1):
        title_index=str(title_index)
        if self.title_dict:
            sub_url="https://tieba.baidu.com/p/%s?pn=%d"%(self.title_dict[title_index][0],page_number)
            req=self.Session().get(sub_url)
            return req
        else:
            print('no title_dict detected,run TiebaList first!')
    def reply(self,index,ptype='reply',*args):
        pass
    def SaverHtml(self,req):
        with open('/tmp/samp.html','w') as fp:
            fp.write(req.text)
            print('save to /tmp/samp.html')
    pass
if __name__ == '__main__':
    samp=BaiduTieba(user=None,passwd=None)
    if len(sys.argv) == 1:
        name=input("请输入贴吧名称:\n")
        samp.TiebaList(name)
    else:
        pass
