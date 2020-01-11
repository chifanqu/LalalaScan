#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
from LalalaScan_ui import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QListWidgetItem
from PyQt5 import QtGui
from lib.core.common import checkUrl
from lib.controller.scanThread        import ScanThread
from lib.controller.timerThread       import TimerThread
from lib.controller.pluginThread      import PluginThread
from lib.controller.pluginTimerThread import PluginTimerThread
from lib.core.data import scan, plugins
from lib.core.pluginManager import PluginManager
from gevent import monkey; monkey.patch_all()

class LalalaScanDesiger(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(LalalaScanDesiger, self).__init__(parent)
        self.setupUi(self)
        self.show()
        self.initWidget()
        self.initConnect()
        self.loadModules()
        self.loadOtherModules()

    def initWidget(self):
        '''
        @description: 初始化控件
        @param {self:QMainWindow}
        @return:
        '''
        # 显示图标
        self.setWindowIcon(QtGui.QIcon('LalalaScan.ico'))
        # 显示标题
        self.setWindowTitle('LalalaScan')
        # 允许textBrowser使用系统浏览器打开链接
        self.textBrowserOutput.setOpenExternalLinks(True)

    def initConnect(self):
        '''
        @description: 初始化 signal 和 slot 的连接
        @param {self:QMainWindow}
        @return:
        '''
        # 开始按钮
        self.pushButtonStart.clicked.connect(self.startBtnClick)
        # 停止按钮
        self.pushButtonStop.clicked.connect(self.stopBtnClick)

    # 开始按钮
    def startBtnClick(self):
        '''
        @description: 开始按钮单击函数
        @param {self:QMainWindow}
        @return:
        '''
        # 获取域名，并进行检查
        baseUrl = self.lineEditInput.text()
        # 检查域名输入是否合法
        baseUrl = checkUrl(baseUrl)
        if baseUrl == '':
            QMessageBox.information(self, "提示", "输入域名有误，请检测~")
            return False
        # 按钮开关
        self.pushButtonStart.setEnabled(False)
        self.pushButtonStop.setEnabled(True)
        # 清空输出框
        self.textBrowserOutput.setHtml
        self.textBrowserOutput.clear()
        # 清空插件的listview
        self.initPluginListWidget()
        # 扫描线程
        self.scanThread = ScanThread()
        self.scanThread.target = baseUrl
        self.scanThread._signalShowScanResult.connect(self.showScanResult) # 连接信号
        self.scanThread._signalScanDone.connect(self.scanDone) # 连接信号
        self.scanThread.start()
        # 状态线程
        self.timerThread = TimerThread()
        self.timerThread._signalShowScanState.connect(self.showScanState) # 连接信号
        self.timerThread._signalShowScanSpeed.connect(self.showScanSpeed) # 连接信号
        self.timerThread.start()
        # 插件线程
        self.pluginTimerThread = PluginTimerThread()
        self.pluginTimerThread._signalPluginAnim.connect(self.pluginAnim) # 连接信号
        self.pluginTimerThread.start()
        self.pluginThread = PluginThread()
        self.pluginThread._signalPluginDone.connect(self.pluginDone) # 连接信号
        self.pluginThread.start()

    def scanDone(self, msg):
        '''
        @description: 扫描完成后，清理下数据
        @param {msg: ''}
        @return:
        '''
        if msg == "requests.exceptions.ConnectionError":
            self.textBrowserOutput.append(u"HTTP连接出错: requests.exceptions.ConnectionError")
            self.stopBtnClick()
            return
        self.timerThread.stopTimer()
        self.showScanState("准备就绪...")
        # 按status code整理下扫描结果
        self.clearOutput()
        statusCodeList = scan.scanResultDict.keys() 
        statusCodeList= sorted(statusCodeList)
        for statusCode in statusCodeList:
            scanResultList = scan.scanResultDict[statusCode]
            for scanResult in scanResultList:
                self.showScanResult({'status':statusCode, 'url':scanResult})
        # 清空扫描数据
        scan.scanResultDict = None
        self.pluginTimerThread.startPluginTimer()
        self.pluginThread.startPlugin()

    def pluginDone(self, msg):
        '''
        @description: 插件扫描完成后，输出
        @param msg: {'name':'', 'outputHTMLList':list()}
        @return:
        '''
        # 显示插件结果
        pluginName     = msg['name']
        outputHTMLList = msg['outputHTMLList']
        doneStat       = '[v]' if len(outputHTMLList) > 0 else '[x]'
        if len(outputHTMLList) > 0:
            # 空一行
            self.textBrowserOutput.append("<a> </a>")
            # 标题
            titleHTML = "<h3>%s</h3>" % pluginName
            self.textBrowserOutput.append(titleHTML)
            # 每行
            for outputHTML in outputHTMLList:
                self.textBrowserOutput.append("<p>"+outputHTML+"</p>")
        # 右侧list显示前缀
        index = plugins.nowIndex - 1
        item = self.listWidgetPlugin.item(index)
        text = doneStat + item.text()[3:]
        item.setText(text)
        # 所有插件均结束
        if plugins.nowIndex == self.listWidgetPlugin.count():
            self.pushButtonStart.setEnabled(True)
            self.pushButtonStop.setEnabled(False)
            self.showScanState("准备就绪...")
            self.pluginTimerThread.stopPluginTimer()

    def pluginAnim(self, msg):
        '''
        @description: 显示插件的运行动画: \ - / 
        @param {msg: ''}
        @return:
        '''
        index = plugins.nowIndex
        count = self.listWidgetPlugin.count()
        # 显示
        if index < count:
            item = self.listWidgetPlugin.item(index)
            text = msg + item.text()[3:]
            item.setText(text)            

    def clearOutput(self):
        '''
        @description: 清空输出框
        @param 
        @return:
        '''
        self.textBrowserOutput.clear()

    def showScanResult(self, resultDict):
        '''
        @description: 显示扫描的结果，status和url
        @param {resultDict:{'status':200,'url':'http://127.0.0.1/'}}
        @return:
        '''
        url    = resultDict['url']
        status = resultDict['status']
        # 颜色
        if status == 200: color = "green"
        else:             color = "red"
        # 输出到文本框
        htmlStr = '<a style="color:%s">%d</a>  |  <a href="%s">%s</a>\r\n' % (color, status, url, url)
        self.textBrowserOutput.append(htmlStr)

    def showScanState(self, nowTask):
        '''
        @description: 显示扫描的网址
        @param {nowTask:'http://127.0.0.1/'}
        @return:
        '''
        speedStr = "扫描信息: %s" % nowTask
        self.labelState.setText(speedStr)

    def showScanSpeed(self, speed):
        '''
        @description: 显示扫描的速度, 100/s
        @param {speed:100}
        @return:
        '''
        speedStr = "扫描速度: %d / s" % speed
        self.labelSpeed.setText(speedStr)

    # 停止按钮
    def stopBtnClick(self):
        '''
        @description: 停止按钮单击函数
        @param {self:QMainWindow}
        @return:
        '''
        # 按钮开关
        self.pushButtonStart.setEnabled(True)
        self.pushButtonStop.setEnabled(False)
        # 关线程
        self.scanThread.stopScan()
        self.timerThread.stopTimer()
        self.pluginTimerThread.stopPluginTimer()
        self.pluginThread.stopPlugin()

    # 加载插件
    def loadModules(self):
        '''
        @description: 加载、显示插件
        @param {self:QMainWindow}
        @return:
        '''
        # 自己写的简单的插件框架
        pluginManager = PluginManager()
        pluginManager.setPluginDir('plugin')
        plugins.pluginDic = pluginManager.getAllPlugins(['getName', 'exploit'])
        # 显示插件
        self.showPlugins(plugins.pluginDic, self.listWidgetPlugin)

    # 初始插件的前缀为[-]
    def initPluginListWidget(self):
        for index in range(self.listWidgetPlugin.count()):
            initStat = "[-]"
            item = self.listWidgetPlugin.item(index)
            text = initStat + item.text()[3:]
            item.setText(text)

    # TODO:加载xray兼容插件
    def loadOtherModules(self):
        '''
        @description: 加载、显示其余模块
        @param {self:QMainWindow}
        @return:
        '''
        pass

    def showPlugins(self, pluginDic, listWidget):
        '''
        @description: 右边栏显示插件
        @param {self:QMainWindow}
        @return:
        '''
        for plugin in pluginDic.values():
            pluginName = plugin.getName()
            item = QListWidgetItem("[-] " + pluginName)
            listWidget.addItem(item)