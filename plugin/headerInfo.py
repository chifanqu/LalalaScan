#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import requests

def getName():
    '''
    @description: 插件名称
    @param
    @return: 
    '''
    return u"Header信息"

def exploit(oriTarget, scanResultAndResponseList):
    '''
    @description: 扫描
    @param: oriTarget - 原始输入,scanResultAndResponseList - 扫描出来地址和response
    @return: html输出,list(), 每行一个~
    '''
    htmlList = []
    for scanResultAndResponse in scanResultAndResponseList:
        target = scanResultAndResponse['target']
        if target == oriTarget:
            response = scanResultAndResponse['response']
            headers = response.headers
            for key, value in headers.items():
                htmlStr = "%s: %s" % (key, value)
                htmlList.append(htmlStr)
    return htmlList

if __name__ == "__main__":
    pass
