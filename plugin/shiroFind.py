#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def getName():
    '''
    @description: 插件名称
    @param
    @return: 
    '''
    return u"shiro"

def exploit(oriTarget, scanResultAndResponseList):
    '''
    @description: 扫描
    @param: oriTarget - 原始输入,scanResultAndResponseList - 扫描出来地址和response
    @return: html输出,list(), 每行一个~
    '''
    htmlList = []
    for scanResultAndResponse in scanResultAndResponseList:
        target = scanResultAndResponse['target']
        response = scanResultAndResponse['response']
        # Set-Cookie: rememberMe=deleteMe
        if  "Set-Cookie" in response.headers and \
            "rememberMe=deleteMe" in response.headers["Set-Cookie"]:
            htmlList.append('<a href="%s">%s</a>' % (target, target))
            # 有一个就行了,退出循环
            break
    return htmlList

if __name__ == "__main__":
    pass
