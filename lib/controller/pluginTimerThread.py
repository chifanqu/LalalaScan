#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtCore import QThread
from PyQt5.QtCore import *
from lib.core.data import scan, conf, plugins
import time

# 继承QThread
class PluginTimerThread(QThread):
    # 通过类成员对象定义信号对象
    _signalPluginAnim = pyqtSignal(str)

    isStop = True
    isStart = False

    animStrList = [" \\ ", "---", " / "]
 
    def __init__(self):
        super(PluginTimerThread, self).__init__()
        plugins.nowIndex = 0
 
    def __del__(self):
        self.wait()

    def stopPluginTimer(self):
        self.isStop = True

    def startPluginTimer(self):
        self.isStart = True

    # 耗时操作放在这
    def run(self):
        # 开启
        self.isStop = False
        self.isStart = False
        while not self.isStart:
            time.sleep(1)
        # 计数
        index = 0
        # 延迟时间
        sleepTime = 0.25
        while not self.isStop:
            index += 1
            animStr = self.animStrList[index % len(self.animStrList)]
            self._signalPluginAnim.emit(animStr)
            time.sleep(sleepTime)

