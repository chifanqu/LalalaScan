#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import requests
import re
import random
import binascii
import string
from bs4 import BeautifulSoup
import socket
from lib.core.data import conf, paths
from lib.utils.config import ConfigFileParser
from lib.core.logger import logger, tracebackLogger
from urllib.parse import urlparse, urljoin


def crc32(content):
    return binascii.crc32(content.encode())

def isPortOpen(target, port):
    '''
    @description: 判断端口是否开放
    @param
    @return: 端口是否开放
    '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        return True if s.connect_ex((target, port)) == 0 else False
    except Exception as e:
        pass
    finally:
        s.close()

def getTargetList(url):
    '''
    @description: 返回url的所有路径
    @param {url:输入的url}
    @return: 返回包含输入所有路径的list
    '''
    urlList = []
    # 先判断是否有协议
    if not re.match(r'^https?://.+', url):
        url = 'http://%s' % url
    try:
        # 尝试解析url
        parsedUrl = urllib.parse.urlparse(url)
        # 检测域名情况
        if parsedUrl.netloc == '': return urlList
        # 检测域名和路径，多重路径均加入 list 中
        if parsedUrl.path != '':
            pathList = parsedUrl.path.split('/')
            # 判断后缀为路径 / 文件
            if pathList[-1] == '' or '.' in pathList[-1]:
                pathList = pathList[:-1]
            # 倒序遍历路径，添加进 list 中
            for i in range(1,len(pathList))[::-1]:
                targetPath = '/'.join(pathList[1:i+1])
                target = "%s://%s/%s/" % (parsedUrl.scheme, parsedUrl.netloc, targetPath)
                urlList.append(target)
        # netloc 加入 list 中
        target = "%s://%s/" % (parsedUrl.scheme, parsedUrl.netloc)
        urlList.append(target)
    except Exception as e:
        tracebackLogger()
        # 识别失败，有多少返回多少吧
        pass
    return urlList

def getSubDirList(url):
    '''
    @description: 返回url的所有子路径   http://127.0.0.1/aaa/bbb/ccc/ddd.php -> aaa bbb ccc
    @param {url:输入的url}
    @return: 返回包含输入所有路径的list
    '''
    subDirList = []
    # 先判断是否有协议
    if not re.match(r'^https?://.+', url):
        url = 'http://%s' % url
    try:
        # 尝试解析url
        parsedUrl = urllib.parse.urlparse(url)
        # 检测域名情况
        if parsedUrl.netloc == '': return subDirList
        # 检测域名和路径，多重路径均加入 list 中
        if parsedUrl.path != '':
            pathList = parsedUrl.path.split('/')
            # 全是路径
            if parsedUrl.endswith('/'):
                subDirList.extend(pathList)
            # 最后一个是文件
            else:
                subDirList.extend(pathList[:-1])
    except Exception as e:
        tracebackLogger()
        # 识别失败，有多少返回多少吧
        pass
    resultList = []
    for subDir in subDirList:
        if subDir == "": resultList.append(subDir)
    return resultList


def checkUrl(url):
    '''
    @description: 检查 url 是否合法
    @param {url:输入的url}
    @return: 整改后的url
    '''
    # 先判断是否有协议
    if not re.match(r'^https?://.+', url):
        url = 'http://%s' % url
    # 尝试解析url
    parsedUrl = urllib.parse.urlparse(url)
    # 检测域名情况
    if parsedUrl.netloc == '': return ''
    return url

def check404Page(url):
    '''
    @description: 检查404页面，收集信息
    @param {url:输入的url}
    @return: 返回:{"isChecked":True, "status":200, "crc32":"xxx"} or {"isChecked":True, "status":404, "crc32":""}
    '''
    checkResult = {"isChecked":False, "status":0, "crc32":""}
    try:
        # 生成随机页面
        randomCollect = string.ascii_letters + string.digits
        randomStr = ''.join(random.sample(randomCollect, random.randint(20,30)))
        randomUrl = "%s%s.html" % (url, randomStr)
        response = requests.get(randomUrl, timeout=3)
        # 检测 status code
        # 如果是 404 ，直接返回就行
        if response.status_code == 404:
            checkResult = {"isChecked":True, "status":404, "crc32":""}
        # 200的话，检查404页面的crc~
        elif response.status_code == 200:
            randomStr_1 = ''.join(random.sample(randomCollect, random.randint(20,30)))
            randomUrl_1 = "%s%s.html" % (url, randomStr)
            response_1  = requests.get(randomUrl_1, timeout=3)
            # 替换掉可能出现的随机字符串...
            path       = urllib.parse.urlparse(randomUrl).path
            path_1     = urllib.parse.urlparse(randomUrl).path
            compText   = response.text
            compText_1 = response_1.text
            compText   = response.text.replace(path, '').replace(randomStr, '')
            compText_1 = response_1.text.replace(path_1, '').replace(randomStr_1, '')
            if crc32(compText) == crc32(compText_1):
                crc32Str = crc32(compText)
                checkResult = {"isChecked":True, "status":200, "crc32":crc32Str}
            # TODO:检查title的指定字符串？
            else:
                pass
        # 不然就搞不定了，后续再研究是否有其他特征~
        else:
            pass
    except Exception as e:
        tracebackLogger()
    
    return checkResult

def getBackendLangByHeaders(headers):
    '''
    @description: 根据返回包的header信息，检查后端语言
    @param {url:输入的url}
    @return: ["php","jsp"]
    '''
    # 后端语言特征
    fingerprintDic = {
        "php":[
            {"X-Powered-By": "PHP"},
            {"Server": "PHP"},
            {"Location": ".php"},
        ],
        '''
        "python":[
            {"Server": "Python"},
            {"Server": "Werkzeug"},
        ],
        '''
        "jsp":[
            {"Server": "Apache-Coyote"},
            {"Server": "Weblogic"},
            {"X-Powered-By": "JSP"},
            {"Set-Cookie": "JSESSION"},
            {"Location": ".jsp"},
            {"Location": ".action"},
            {"Location": ".do"},
        ],
        "asp":[
            {"Server": "IIS"},
            {"X-Powered-By": "ASP"},
            {"Location": ".asp"},
        ],
        "aspx":[
            {"Server": "IIS"},
            {"X-Powered-By": "ASP"},
            {"Location": ".aspx"},
        ],
    }
    backendLangList = []
    for backendLang, fingerprintList in fingerprintDic.items():
        for fingerprint in fingerprintList:
            headerName, headerKeyWord = list(fingerprint.items())[0]
            if headerName in headers and headerKeyWord.lower() in headers[headerName].lower():
                backendLangList.append(backendLang)
                break
    return backendLangList

def getBackendLangByText(pageText):
    '''
    @description: TODO:根据返回包的内容信息，检查后端语言
    @param {url:页面的内容pageText}
    @return: ["php","jsp"]
    '''
    return []

def getBackendLangByGuess(url, text, alreadyFindExtList):
    '''
    @description: 根据返回包的内容信息，检查后端语言
    @param {url:页面的内容pageText}
    @return: ["php","jsp"]
    '''
    backendLangList = []
    extList = ['php', 'jsp', 'asp', 'aspx']
    # 原 url 可能有扩展名啥的？先整理出目录
    if '.' in url.split('/')[-1]: 
        url = '/'.join(url.split('/')[:-1])
    for ext in extList:
        if ext not in alreadyFindExtList:
            guessUrl = "%sindex.%s" % (url, ext)
            try:
                response = requests.get(guessUrl, timeout=3)
                guessText = response.text
                if guessText == text: backendLangList.append(ext)
            except Exception as e:
                pass
    return backendLangList

def getBackendLang(url):
    '''
    @description: 检查后端语言，为字典做准备
    @param {url:输入的url}
    @return: "php" / "jsp" ... , 找不到就返回空字符串
    '''
    backendLangList = list()
    # 0、先看下url是不是自带扩展名了额~
    extList = ['php', 'jsp', 'asp', 'aspx']
    for ext in extList:
        if url.lower().endswith('.'+ext): 
            backendLangList.append(ext)
            # 自带扩展名的还检查啥，直接返回吧~
            return backendLangList
    try:
        response = requests.get(url, allow_redirects=False, timeout=3)
    except Exception as e:
        return []
    # 1、根据 headers 判断
    headers = response.headers
    backendLangByHeadersList = getBackendLangByHeaders(headers)
    backendLangList.extend(backendLangByHeadersList)
    # 2、根据页面内容判断扩展名，类似爬虫？
    # 由于禁用了重定向，如果为 3xx,就重新请求一次内容
    if response.status_code / 100 == 3:
        response = requests.get(url, timeout=3)
    pageText = response.text
    backendLangByTextList = getBackendLangByText(pageText)
    backendLangList.extend(backendLangByTextList)
    # 3、根据 index.xxx 和文件路径返回值差异来判断~
    backendLangByGuessList = getBackendLangByGuess(url, pageText, backendLangList)
    backendLangList.extend(backendLangByGuessList)
    # 去重
    backendLangList = list(set(backendLangList))
    return backendLangList
    
def getPayloadByExtList(dictDir, extList):
    '''
    @description: 根据扩展名来生成文件名字典
    @param {list:['php','jsp']}
    @return: 返回list
    '''
    payloadList = list()
    # 静态，无扩展名的
    if conf.dict_mode:
        dictPayloadList = loadMultDict(dictDir)
        payloadList.extend(dictPayloadList)
    # 自定义通用扩展名
    if conf.fuzz_mode:
        # 后端语言扩展名
        mainFileDict = conf.fuzz_mode_load_main_dict
        extDict = conf.fuzz_mode_load_ext_dict
        fuzzPayloadList = loadFuzzDict(mainFileDict, extDict, extList)
        payloadList.extend(fuzzPayloadList)
    return payloadList

def loadFuzzDict(mainFileDict, extDict, extList):
    '''
    @description: 生成 fuzz 文件
    @param {mainFileDict:文件名所在文件, extDict:通用扩展名所在文件, extList:后端语言扩展名列表}
    @return: 所有文件名存储的List
    '''
    payloadList = list()
    # 不能确定后端语言的扩展名的话，就都用 TODO:固化在配置中
    if len(extList) == 0: extList = ['php', 'jsp', 'asp', 'aspx']
    # 读通用扩展名
    extFileList = loadSingleDict(extDict)
    extList.extend(extFileList)
    # 读文件名
    mainFileList = loadMultDict(mainFileDict)
    # 根据扩展扩展
    for mainFile in mainFileList:
        for ext in extList:
            payload = "%s.%s" % (mainFile, ext)
            payloadList.append(payload)
    return payloadList

def loadSingleDict(path):
    '''
    @description: 添加单个字典文件
    @param {path:字典文件路径}
    @return:
    '''
    try:
        # 加载文件
        with open(path) as single_file:
            return single_file.read().splitlines()
    except Exception as e:
        tracebackLogger()
        return []

def loadMultDict(path):
    '''
    @description: 添加多个字典文件
    @param {path:字典文件路径}
    @return: list:文件夹下字典文件每行的内容
    '''
    tmpList = []
    try:
        for filename in os.listdir(path):
            tmpList.extend(loadSingleDict(os.path.join(path, filename)))
        return tmpList
    except Exception as e:
        tracebackLogger()
        return []

def setPaths():
    """
    设置全局绝对路径
    """
    # 根目录
    root_path = paths.ROOT_PATH
    # 文件目录
    paths.DATA_PATH = os.path.join(root_path, "data")
    paths.OUTPUT_PATH = os.path.join(root_path, "output")
    paths.CONFIG_PATH = os.path.join(root_path, "lalalaScan.conf")
    paths.UA_LIST_PATH = os.path.join(paths.DATA_PATH, "user-agents.txt")

    if not os.path.exists(paths.OUTPUT_PATH):
        os.mkdir(paths.OUTPUT_PATH)
    if not os.path.exists(paths.DATA_PATH):
        os.mkdir(paths.DATA_PATH)

    if os.path.isfile(paths.CONFIG_PATH):
        pass
    else:
        msg = 'Config files missing!'
        logger.error(msg)
        sys.exit(0)


def loadConf():
    '''
    @description: 加载扫描配置(以后将使用参数，而非从文件加载)
    @param {}
    @return: None
    '''
    conf.dict_mode = eval(ConfigFileParser().dict_mode())
    conf.dict_mode_load_dir_dict = os.path.join(paths.DATA_PATH,eval(ConfigFileParser().dict_mode_load_dir_dict()))
    conf.dict_mode_load_mult_dict = os.path.join(paths.DATA_PATH,eval(ConfigFileParser().dict_mode_load_mult_dict()))
    
    conf.fuzz_mode = eval(ConfigFileParser().fuzz_mode())
    conf.fuzz_mode_load_main_dict = os.path.join(paths.DATA_PATH, eval(ConfigFileParser().fuzz_mode_load_main_dict()))
    conf.fuzz_mode_load_ext_dict = os.path.join(paths.DATA_PATH, eval(ConfigFileParser().fuzz_mode_load_ext_dict()))

    conf.request_headers = eval(ConfigFileParser().request_headers())
    conf.request_header_ua = eval(ConfigFileParser().request_header_ua())
    conf.request_header_cookie = eval(ConfigFileParser().request_header_cookie())
    conf.request_header_401_auth = eval(ConfigFileParser().request_header_401_auth())
    conf.request_timeout = eval(ConfigFileParser().request_timeout())
    conf.request_delay = eval(ConfigFileParser().request_delay())
    conf.request_limit = eval(ConfigFileParser().request_limit())
    conf.request_persistent_connect = eval(ConfigFileParser().request_persistent_connect())
    conf.request_method = eval(ConfigFileParser().request_method())

    conf.proxy_server = eval(ConfigFileParser().proxy_server())


class LinksParser(object):
    """
    docstring for link_parser
    """
    def __init__(self, response):
        super(LinksParser, self).__init__()
        self.response = response
        self.url     = self.response.url
        self.baseurl = self.getBaseurl(self.url)
        self.soup    = BeautifulSoup(self.response.text, 'lxml')
        self.allList = []

    def getBaseurl(self, link):
        netloc = urlparse(link).netloc
        if netloc:
            split_url = link.split(netloc)
            baseurl = '%s%s' % (split_url[0], netloc)
            return baseurl

    def completUrl(self, link):
        if link.startswith('/') or link.startswith('.'):
            return urljoin(self.baseurl, link)
        elif link.startswith('http') or link.startswith('https'):
            return link
        elif link == '#':
            return False
        elif link.startswith('#'):
            return urljoin(self.url, link)
        else:
            return False

    def getAllResult(self):
        self.getSrc()
        self.getHref()
        self.getTagForm()
        self.allList = list(set(self.allList))
        return self.allList

    def getTagA(self):
        # 处理A链接
        linkList = []
        for tag in self.soup.find_all('a'):
            if 'href' in tag.attrs:
                link = tag.attrs['href']
                completLink = self.completUrl(link.strip())
                if completLink:
                    linkList.append(completLink)
        self.allList.extend(linkList)
        return linkList

    def getTagLink(self):
        # 处理link链接资源
        linkList = []
        for tag in self.soup.find_all('link'):
            if 'href' in tag.attrs:
                link = tag.attrs['href']
                completLink = self.completUrl(link.strip())
                if completLink:
                    linkList.append(completLink)
        self.allList.extend(linkList)
        return linkList

    def getTagImg(self):
        # 处理img链接资源
        linkList = []
        for tag in self.soup.find_all('img'):
            if 'src' in tag.attrs:
                link = tag.attrs['src']
                completLink = self.completUrl(link.strip())
                if completLink:
                    linkList.append(completLink)
        self.allList.extend(linkList)
        return linkList

    def getTagScript(self):
        # 处理script链接资源
        linkList = []
        for tag in self.soup.find_all('script'):
            if 'src' in tag.attrs:
                link = tag.attrs['src']
                completLink = self.completUrl(link.strip())
                if completLink:
                    linkList.append(completLink)
        self.allList.extend(linkList)
        return linkList

    def getTagForm(self):
        # 处理form链接资源
        linkList = []
        for tag in self.soup.find_all('form'):
            if 'action' in tag.attrs:
                link = tag.attrs['action']
                completLink = self.completUrl(link.strip())
                if completLink:
                    linkList.append(completLink)
        self.allList.extend(linkList)
        return linkList

    def getSrc(self):
        # 处理src属性
        linkList = []
        for tag in self.soup.find_all(attrs={"src":True}):
            link = tag.attrs['src']
            completLink = self.completUrl(link.strip())
            if completLink:
                linkList.append(completLink)
        self.allList.extend(linkList)
        return linkList

    def getHref(self):
        # 处理href属性
        linkList = []
        for tag in self.soup.find_all(attrs={"href":True}):
            link = tag.attrs['href']
            completLink = self.completUrl(link.strip())
            if completLink:
                linkList.append(completLink)
        self.allList.extend(linkList)
        return linkList

if __name__ == "__main__":
    paths.ROOT_PATH = os.getcwd() 
    setPaths()
    loadConf()
    url = "http://127.0.0.1:335/"
    lp = LinksParser(requests.get(url))
    print(lp.getAllResult())