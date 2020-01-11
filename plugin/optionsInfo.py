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
    return u"OPTIONS信息"

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
    url = "%s://%s/" % (scheme, netloc)
    response = requests.options(url)
    headers = response.headers
    if 'Allow' in headers:
        allow = headers['Allow']
        methodList = ['PUT', 'COPY', 'MOVE', 'DELETE', 'MKCOL']
        for method in methodList:
            allow = allow.replace(method, '<a style="red">%s</a>'%method)
        htmlList.append(allow)
    return htmlList

if __name__ == "__main__":
    pass
