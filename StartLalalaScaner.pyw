#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import re
import time
import urllib
from lalalaScan import LalalaScanDesiger
from PyQt5.QtWidgets import QApplication
from lib.core.data import paths
from lib.core.common import setPaths, loadConf

if __name__ == "__main__":

    # 设置全局路径
    paths.ROOT_PATH = os.getcwd() 
    setPaths()

    # 加载配置文件
    loadConf()

    app = QApplication(sys.argv)
    ui = LalalaScanDesiger()
    sys.exit(app.exec_())