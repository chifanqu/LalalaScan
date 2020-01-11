#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtCore import QThread
from PyQt5.QtCore import *
from lib.core.data import scan, conf, plugins
import time

# 继承QThread
class PluginThread(QThread):
    # 通过类成员对象定义信号对象
    _signalPluginDone = pyqtSignal(dict)

    isStop  = True
    isStart = False
 
    def __init__(self):
        super(PluginThread, self).__init__()
 
    def __del__(self):
        self.wait()

    def stopPlugin(self):
        self.isStop = True

    def startPlugin(self):
        self.isStart = True

    # 耗时操作放在这
    def run(self):
        # 开启
        self.isStop  = False
        self.isStart = False
        while not self.isStart:
            time.sleep(1)
        # 遍历执行插件的exploit方法
        for index, key in enumerate(plugins.pluginDic.keys()):
            if self.isStop: break
            pluginStratTime = time.time()   # 插件开始时间
            plugin = plugins.pluginDic[key]
            pluginName = plugin.getName()
            outputHTMLList = plugin.exploit(scan.oriTarget, scan.scanResultAndResponseList)
            pluginEndTime = time.time()     # 插件结束时间
            # 控制下每个插件的运行时间，> 1s
            if pluginEndTime - pluginStratTime < 1: time.sleep(1)
            # 下一个插件
            plugins.nowIndex = index + 1
            # 发送插件结束信号
            if self.isStop: break
            self._signalPluginDone.emit({"name":pluginName, "outputHTMLList":outputHTMLList})

