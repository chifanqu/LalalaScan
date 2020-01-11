#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import requests
import urllib
import socket
from bs4 import BeautifulSoup
import re
import sys
import gevent
from gevent.queue import Queue

def getName():
    '''
    @description: 插件名称
    @param
    @return: 
    '''
    return u"端口扫描"

class PostScaner():

    target = ""
    portQueue = Queue()
    resultQueue = Queue()

    def __init__(self, target, portConf):
        self.target = target
        portList = self.parsePort(portConf)
        for port in portList:
            self.portQueue.put(port)

    def isPortOpen(self, target, port):
        '''
        @description: 端口扫描
        @param
        @return: 端口是否开放
        '''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            return True if s.connect_ex((target, port)) == 0 else False
        except Exception as e:
            pass
        finally:
            s.close()

    def getHttpBanner(self, url):
        '''
        @description: 获取HTTP信息
        @param
        @return: banner
        '''
        try:
            r = requests.get(url, timeout=2, verify=False, allow_redirects=True)
            soup = BeautifulSoup(r.content,'lxml')
            return soup.title.text.strip('\n').strip()
        except Exception as e:
            pass

    def getSocketBanner(self, target, port):
        '''
        @description: 获取socket信息
        @param
        @return: banner
        '''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect(target, port)
            s.send('HELLO\r\n')
            return s.recv(1024).split('\r\n')[0].strip('\r\n')
        except Exception as e:
            pass
        finally:
            s.close()

    def parsePort(self, portStr):
        '''
        @description: 解析端口, 例如: 21,22,23,80-89,8000-9000
        @param
        @return: banner
        '''
        portList = []
        portInfoList = portStr.split(',')
        for portInfo in portInfoList:
            if re.match(r'^\d+$', portInfo): 
                portList.append(int(portInfo))
            elif re.match(r'^\d+-\d+$', portInfo):
                startPort = int(portInfo.split('-')[0])
                endPort   = int(portInfo.split('-')[-1])+1
                for port in range(startPort, endPort):
                    portList.append(port)
        return portList

    def worker(self):
        '''
        @description: 封包发包穷举器
        @param {type}
        @return:
        '''
        target = self.target
        port   = self.portQueue.get()
        isOpen = self.isPortOpen(target, port)
        if not isOpen: return
        banner = self.getHttpBanner('http://%s:%s' % (target, port))
        # http
        if banner:
            result = '[+]%s ---- open   %s' % (str(port).rjust(5), banner[:18])
            self.resultQueue.put(result)
            return
        # https
        banner = self.getHttpBanner('https://%s:%s' % (target, port))
        if banner:
            result = '[+]%s ---- open   %s' % (str(port).rjust(5), banner[:18])
            self.resultQueue.put(result)
            return
        # socket
        banner = self.getSocketBanner(target, port)
        if banner:
            result = '[+]%s ---- open   %s' % (str(port).rjust(5), banner[:18])
            self.resultQueue.put(result)
            return
        # 空
        else:
            result = '[+]%s ---- open' % (str(port).rjust(5))
            self.resultQueue.put(result)
            return
        
    def boss(self):
        '''
        @description: worker控制器
        @param {type}
        @return:
        '''
        while not self.portQueue.empty():
            self.worker()
    
    def scan(self):
        '''
        @description: 扫描端口
        @param
        @return: 
        '''
        while not self.portQueue.empty():
            allTask = [gevent.spawn(self.boss) for i in range(30)]
            gevent.joinall(allTask)
        resultList = list(self.resultQueue.queue)
        self.resultQueue.queue.clear()
        return resultList

def exploit(oriTarget, scanResultAndResponseList):
    '''
    @description: 扫描
    @param: oriTarget - 原始输入,scanResultAndResponseList - 扫描出来地址和response
    @return: html输出,list(), 每行一个~
    '''
    portConf = "21,22,23,80,335,443,1521,3306,3389,6379,8000-8999"

    htmlList = []
    netloc = urllib.parse.urlparse(oriTarget).netloc
    target = netloc.split(":")[0]   # 获取不带端口的目标
    
    portScaner = PostScaner(target, portConf)
    tmpList = portScaner.scan()

    for tmp in tmpList:
        htmlList.append('<span style="white-space:pre">%s</span>' % tmp)
    
    return htmlList

if __name__ == "__main__":
    #exit()
    from gevent import monkey; monkey.patch_all()
    htmlList = exploit("http://192.168.201.130:335/", [])
    for html in htmlList:
        print(html)
