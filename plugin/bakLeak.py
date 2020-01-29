#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import requests
from urllib.parse import urlparse

def getName():
    '''
    @description: 插件名称
    @param
    @return: 
    '''
    return u"备份文件泄露"


def getBakUrl(url):
    '''
    @description: 获取敏感文件的url
    @param: url
    @return: list()
    '''
    resultList = []
    tmpList  = url.split('/')
    dirpath  = '/'.join(tmpList[:-1])   # 目录
    filename = tmpList[-1]              # 文件
    mainName = '.'.join(filename.split('/')[:-1])  # 主文件名
    extName  = filename.split('/')[-1]             # 扩展名
    # .index.php.swp / swo / swn
    resultList.append(dirpath+'/.'+filename+'.swp')
    resultList.append(dirpath+'/.'+filename+'.swo')
    resultList.append(dirpath+'/.'+filename+'.swn')
    # index.bak
    resultList.append(dirpath+'/'+filename+'.bak')
    resultList.append(dirpath+'/'+mainName+'.bak')
    resultList.append(dirpath+'/'+filename+'.BAK')
    resultList.append(dirpath+'/'+mainName+'.BAK')
    # index.php~
    resultList.append(dirpath+'/'+filename+'~')
    return resultList

def exploit(oriTarget, scanResultAndResponseList):
    '''
    @description: 扫描
    @param: oriTarget - 原始输入,scanResultAndResponseList - 扫描出来地址和response
    @return: html输出,list(), 每行一个~
    '''
    leakUrlList = []
    for scanResultAndResponse in scanResultAndResponseList:
        target = scanResultAndResponse['target']
        # 判断是否为文件,也需要有path
        if not target.endswith('/') and urlparse(target).path != '':
            urlList = getBakUrl(target)
            # 访问
            for url in urlList:
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        leakUrlList.append(url)
                except Exception as e:
                    print('[x] error:{}'.format(e))
                finally:
                    pass
    htmlList = []
    leakUrlList = list(set(leakUrlList)) # 去重
    for leakUrl in leakUrlList:
        htmlList.append('<a href="%s">%s</a>' % (leakUrl, leakUrl))
    return htmlList

if __name__ == "__main__":
    pass
