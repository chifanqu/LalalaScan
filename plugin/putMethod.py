#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import requests
import urllib
import random
import string

def getName():
    '''
    @description: 插件名称
    @param
    @return: 
    '''
    return u"PUT尝试"

def exploit(oriTarget, scanResultAndResponseList):
    '''
    @description: 扫描
    @param: oriTarget - 原始输入,scanResultAndResponseList - 扫描出来地址和response
    @return: html输出,list(), 每行一个~
    '''
    htmlList = []
    urlParse = urllib.parse.urlparse(oriTarget)
    scheme = urlParse.scheme
    netloc = urlParse.netloc
    randomStr1 = ''.join(random.sample(string.ascii_letters + string.digits, random.randint(20,30)))
    randomStr2 = 'PUT success! ' + ''.join(random.sample(string.ascii_letters + string.digits, random.randint(20,30)))
    url = "%s://%s/%s" % (scheme, netloc, randomStr1)
    try:
        response = requests.put(url, data=randomStr2)
        if response.status_code == 201:
            htmlList.append('status code: 201 Created')
        response = requests.get(url, data=randomStr2)
        if response.status_code == 200 or response.text == randomStr2:
            htmlList.append('<a href="%s">%s</a>' % (url, url))
    except Exception as e:
        print('[x] error:{}'.format(e))
    finally:
        pass
    return htmlList

if __name__ == "__main__":
    pass
