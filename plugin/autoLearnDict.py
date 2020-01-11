#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import requests
from lib.core.common import getSubDirList, loadMultDict, loadSingleDict
from lib.core.data import conf
import os

def getName():
    '''
    @description: 插件名称
    @param
    @return: 
    '''
    return u"自学习字典"

def exploit(oriTarget, scanResultAndResponseList):
    '''
    @description: 扫描
    @param: oriTarget - 原始输入,scanResultAndResponseList - 扫描出来地址和response
    @return: html输出,list(), 每行一个~
    '''
    htmlList = []
    autoUpdateFile = "autoUpdate.txt"
    dirList          = []
    payloadList      = []
    mainFilenameList = []
    for scanResultAndResponse in scanResultAndResponseList:
        target  = scanResultAndResponse['target']
        # 加一遍路径
        tmpList = getSubDirList(target)
        dirList.extend(tmpList)
        # 文件
        if not target.endswith('/'):
            payload = target.split('/')[-1]
            mainFilename = payload.split('.')[0]
            payloadList.append(payload)
            mainFilenameList.append(mainFilename)
      
    # 去重
    dirList          = list(set(dirList))
    payloadList      = list(set(payloadList))
    mainFilenameList = list(set(mainFilenameList))

    # 获取原字典的数据
    oriDirList          = loadMultDict(conf.dict_mode_load_dir_dict)
    oriPayloadList      = loadMultDict(conf.dict_mode_load_mult_dict)
    oriMainFilenameList = loadMultDict(conf.fuzz_mode_load_main_dict)

    # 获取需要添加的数据
    updateDirList          = []
    updatePayloadList      = []
    updateMainFilenameList = []
    for dir in dirList:
        if not dir in oriDirList: updateDirList.append(dir)
    for payload in payloadList:
        if not payload in oriPayloadList: updatePayloadList.append(payload)
    for mainFilename in mainFilenameList:
        if not mainFilename in oriMainFilenameList: updateMainFilenameList.append(mainFilename)

    # 加到文件中
    dirAutuFile = os.path.join(conf.dict_mode_load_dir_dict, autoUpdateFile)
    with open(dirAutuFile, 'a+') as f:
        for dir in updateDirList:
            if dir != '': f.write(dir + '\r\n')
        f.close()
    payloadAutuFile = os.path.join(conf.dict_mode_load_mult_dict, autoUpdateFile)
    with open(payloadAutuFile, 'a+') as f:
        for payload in updatePayloadList: 
            if payload != '': f.write(payload + '\r\n')
        f.close()
    mainFilenameAutuFile = os.path.join(conf.fuzz_mode_load_main_dict, autoUpdateFile)
    with open(mainFilenameAutuFile, 'a+') as f:
        for mainFilename in updateMainFilenameList: 
            if mainFilename != '': f.write(mainFilename + '\r\n')
        f.close()

    # 输入的内容
    if len(updateDirList) > 0:          htmlList.append(u'新增 [路径] %d 条...' % len(updateDirList))
    if len(updatePayloadList) > 0:      htmlList.append(u'新增 [字典] %d 条...' % len(updatePayloadList))
    if len(updateMainFilenameList) > 0: htmlList.append(u'新增 [主文件名] %d 条...' % len(updateMainFilenameList))

    return htmlList

if __name__ == "__main__":
    pass
