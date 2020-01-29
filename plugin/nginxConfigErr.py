#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import urllib
import requests

def getName():
    '''
    @description: 插件名称
    @param
    @return: 
    '''
    return u"Nginx目录遍历"

def exploit(oriTarget, scanResultAndResponseList):
    '''
    @description: 扫描
    @param: oriTarget - 原始输入,scanResultAndResponseList - 扫描出来地址和response
    @return: html输出,list(), 每行一个~
    '''
    urlList = []
    for scanResultAndResponse in scanResultAndResponseList:
        target = scanResultAndResponse['target']
        # 判断是否为目录,也不能是域名那个目录...
        if target.endswith('/') and urllib.parse.urlparse(target).path != "/":
            url = target[:-1] + '../'
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    urlList.append(url)
            except Exception as e:
                print('[x] error:{}'.format(e))
            finally:
                pass
    htmlList = []
    urlList = list(set(urlList)) # 去重
    for url in urlList:
        htmlList.append('<a href="%s">%s</a>' % (url, url))
    return htmlList

if __name__ == "__main__":
    pass
