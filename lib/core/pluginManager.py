#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import importlib

class PluginManager():

    pluginList = []
    pluginDir  = None

    def setPluginDir(self, pluginDir):
        '''
        @description: 设置加载插件的目录
        @param: dir
        @return:
        '''
        if not os.path.exists(pluginDir): return False
        self.pluginDir = pluginDir
        return True

    def getAllPlugins(self, attrFilter=['getName']):
        '''
        @description: 加载所有的插件
        @param: attrFilter, 是否存在对应的方法
        @return:
        '''
        pluginDict = {}
        if self.pluginDir == None: return pluginList
        # 遍历文件夹
        for root, dirs, files in os.walk(self.pluginDir):
            for pluginFile in files:
                if not self.isPluginFile(pluginFile): continue
                plugin = importlib.import_module(self.pluginDir + '.' + pluginFile[:-3])
                hasAllAttr = True
                # 判断是否有所有的方法
                for attr in attrFilter:
                    if not hasattr(plugin, attr): 
                        hasAllAttr = False
                        continue
                if not hasAllAttr: continue
                # 获取名称
                pluginName = plugin.getName()
                pluginDict[pluginName] = plugin
        return pluginDict

    def isPluginFile(self, filename):
        '''
        @description: 判断是否为插件
        @param: 
        @return:
        '''
        result = True
        if filename == "__init__.py": result = False
        if not filename.endswith('.py'): result = False
        return result

