#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtCore import QThread
from PyQt5.QtCore import *
from lib.core.data import scan, conf
import time

# 继承QThread
class TimerThread(QThread):
    # 通过类成员对象定义信号对象
    _signalShowScanState = pyqtSignal(str)
    _signalShowScanSpeed = pyqtSignal(int)
    isStop = True
 
    def __init__(self):
        super(TimerThread, self).__init__()
 
    def __del__(self):
        self.wait()

    def stopTimer(self):
        self.isStop = True

    # 耗时操作放在这
    def run(self):
        # 开启
        self.isStop = False
        # 计数
        index = 0
        # 上次扫描计数
        lastScanCount = 0
        # 延迟时间
        sleepTime = 0.05
        while not self.isStop:
            index += 1
            # 1s显示一次速度
            if index % int(1/sleepTime) == 0:
                nowScanCount  = scan.taskCount
                scanCount     = nowScanCount - lastScanCount
                lastScanCount = nowScanCount
                self._signalShowScanSpeed.emit(scanCount)
            # 显示当前扫描内容
            nowTask = scan.nowTask
            if nowTask != None:
                self._signalShowScanState.emit(nowTask)
            time.sleep(sleepTime)
        # 还原状态
        self._signalShowScanSpeed.emit(0)

