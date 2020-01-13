#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import re
from PyQt5.QtCore import QThread
import urllib
from PyQt5.QtCore import *
from lib.core.common import getTargetList, check404Page, getBackendLang, loadConf, getPayloadByExtList, loadSingleDict, loadMultDict, crc32
from lib.core.common import LinksParser, isPortOpen
from lib.core.data import scan, conf
import gevent
import requests
import random
import time
from gevent.queue import Queue

# 继承QThread
class ScanThread(QThread):
    # 通过类成员对象定义信号对象
    _signalShowScanResult = pyqtSignal(dict)
    _signalScanDone = pyqtSignal(str)
    target = ''
    isStop = True
 
    def __init__(self):
        super(ScanThread, self).__init__()
        scan.taskCount = 0
 
    def __del__(self):
        self.wait()

    def stopScan(self):
        self.isStop = True
        if scan.taskQueue != None:
            scan.taskQueue.empty()

    def responseHandler(self, url, response):
        '''
        @description: 处理响应结果
        @param {type}
        @return:
        '''
        responseText = response.text
        # 自动识别404 - 判断是否与获取404页面特征匹配
        check404Result = scan.check404Result
        if response.status_code == 404: return
        if check404Result['isChecked']:
            for checkInfo in check404Result['checkList']:
                if response.status_code == checkInfo['status']:
                    # 没有crc32校验，直接判断为404
                    if checkInfo['status'] == '': return
                    else:
                        path = urllib.parse.urlparse(url).path
                        filename = path.split('/')[-1]
                        compText = responseText.replace(path, '').replace(filename, '')
                        if crc32(compText) == checkInfo['crc32'] or crc32(responseText) == checkInfo['crc32']: return

        # 处理403的问题
        if response.status_code == 403:
            # 文件403 不要了
            if not url.endswith('/'): 
                return
            # TODO:文件夹403，仅发送扫描结果，其余暂不处理
            if url.endswith('/'): 
                self.saveScanResult(url, response)
                return

        # 400 bad request, 不要了
        if response.status_code == 400: return
        
        self.saveScanResult(url, response)

        # 如果是目录，加到target中扫描
        if url.endswith('/'):
            # 递归目录
            for dir in scan.dirList:
                target = url + dir
                self.putToTaskQueue(target)
            # 递归文件
            for payload in scan.payloadList:
                target = url + payload
                self.putToTaskQueue(target)

        # 有内容的话，爬
        if responseText != '':
            # crawl
            crawlTargetList = LinksParser(response).getAllResult()
            for target in crawlTargetList:
                # 检测下是不是一个域名的额，不要打歪了
                if urllib.parse.urlparse(target).netloc != scan.netloc: continue
                # 只要 # 前面的数据
                if "#" in target: target = target.split('#')[0]
                # 本体加入
                self.putToTaskQueue(target)
                # 本体解析得到的路径加入
                tmpTargetList = getTargetList(target)
                self.putToTaskQueue(tmpTargetList)

    def saveScanResult(self, url, response):
        '''
        @description: 扫描得到地址，进行一系列的处理
        @param {url, status}
        @return: None
        '''
        self.showScanResult(url, response.status_code) # 信号发送
        # 加到扫描结果中
        if response.status_code not in scan.scanResultDict:
            scan.scanResultDict[response.status_code] = [url]
        else:
            scan.scanResultDict[response.status_code].append(url)
        # 加到给插件的结果中
        scan.scanResultAndResponseList.append({"target":url, "response":response})

    def showScanResult(self, url, status):
        '''
        @description: 发送信号给主线程，显示发现的url和status_code
        @param {url, status}
        @return: None
        '''
        scanResult = {'url':url, 'status':status}
        self._signalShowScanResult.emit(scanResult) # 信号发送

    def putToTaskQueue(self, t):
        '''
        @description: 添加到任务队列中，顺便判断下是否已经加过队列
        @param {t: target / targetList}
        @return: None
        '''
        if isinstance(t, list):
            for target in t:
                if target in scan.targetDict:
                    pass
                else:
                    scan.targetDict[target] = True
                    scan.taskQueue.put(target)
        else:
            if t in scan.targetDict:
                pass
            else:
                scan.targetDict[t] = True
                scan.taskQueue.put(t)

    def setTarget(self, target):
        '''
        @description: 设置Qedit里面目标
        @param {type}
        @return: None
        '''
        self.target = target

    def worker(self):
        '''
        @description: 封包发包穷举器
        @param {type}
        @return:
        '''
        currentTaskURL = scan.taskQueue.get()
        # 最新在执行的任务
        scan.nowTask = currentTaskURL
        scan.taskCount += 1
        # 自定义 headers
        headers = {}
        if conf.request_headers:
            for header in conf.request_headers.split(','):
                k, v = header.split('=')
                headers[k] = v
        # 自定义 User-Agent
        if conf.request_header_ua:
            headers['User-Agent'] = conf.request_header_ua
        # 自定义cookie
        if conf.request_header_cookie:
            headers['Cookie'] = conf.request_header_cookie

        # 延迟请求
        if conf.request_delay:
            random_sleep_second = random.randint(0, abs(conf.request_delay))
            time.sleep(random_sleep_second)
        # 发包
        try:
            response = requests.request(conf.request_method, currentTaskURL, headers=headers, timeout=conf.request_timeout, verify=False, allow_redirects=conf.redirection_302, proxies=conf.proxy_server)
            # 进入结果处理流程
            self.responseHandler(currentTaskURL, response)
        except requests.exceptions.Timeout as e:
            # TODO:超时处理
            pass
        except Exception as e:
            print('[x] error:{}'.format(e))
        finally:
            # 更新进度
            pass

    def boss(self):
        '''
        @description: worker控制器
        @param {type}
        @return:
        '''
        while not scan.taskQueue.empty() and not self.isStop:
            self.worker()

    # 耗时操作放在这
    def run(self):
        # 目标的域名，防止爬虫打歪
        scan.netloc = urllib.parse.urlparse(self.target).netloc

        # 先看下能不能访问, 多次检测
        isOpen = False
        checkNum = 3
        errorNum = 0
        for i in range(checkNum):
            try:
                response = requests.get(self.target, timeout=5)
                isOpen = True
                break
            except requests.exceptions.ConnectionError:
                errorNum += 1
        if errorNum == checkNum:
            self._signalScanDone.emit("requests.exceptions.ConnectionError")
            return

        # 开启
        self.isStop = False
        # 识别路径，将所有目标路径加入列表
        targetList = getTargetList(self.target)
        # 识别后端语言
        extList = getBackendLang(self.target)
        # 根据后端语言，生成[文件名]字典
        payloadList = getPayloadByExtList(conf.dict_mode_load_mult_dict, extList)
        # 生成路径字典
        dirList = []
        tmpDirList = loadMultDict(conf.dict_mode_load_dir_dict) # loadSingleDict(conf.dict_mode_load_dir_dict)
        for dir in tmpDirList:
            if not dir.endswith('/'): dirList.append(dir)
        # 识别404页面
        check404Result = check404Page(targetList[0])
        # TODO:无法判断404页面
        if not check404Result['isChecked']:
            pass
        
        # 所需的配置，加载到 scan 中
        scan.taskQueue  = Queue()
        scan.taskCount  = 0
        scan.taskLength = 0

        # 保存所有任务的字典，用于判断是否重复
        scan.targetDict = {}

        # 保存所有扫描到的结果，用于整理输出
        scan.scanResultDict = {}

        # 保存扫描的url 和 访问结果，用于后续插件
        scan.scanResultAndResponseList = []

        # 保存最初的扫描目标
        scan.oriTarget = self.target

        # 最原始的target，如果是文件不在target里面，就加到task
        if self.target not in targetList:
            self.putToTaskQueue(self.target)
        # 起码对路径扫一次全的吧，御剑的功能
        for dir in dirList:
            target = targetList[0] + dir
            self.putToTaskQueue(target)
        # 递归文件
        for payload in payloadList:
            target = targetList[0] + payload
            self.putToTaskQueue(target)
        # 把路径的target扔进去
        for target in targetList:
            self.putToTaskQueue(target)

        scan.check404Result = check404Result

        scan.dirList     = dirList
        scan.payloadList = payloadList

        # requests初始化
        requests.packages.urllib3.disable_warnings()
        # 开协程处理...
        while not scan.taskQueue.empty() and not self.isStop:
            allTask = [gevent.spawn(self.boss) for i in range(conf.request_limit)]
            gevent.joinall(allTask)
        # 结束后发个信息
        self._signalScanDone.emit("")

