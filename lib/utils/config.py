#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from configparser import ConfigParser
from lib.core.data import paths
from lib.core.logger import tracebackLogger

# TODO:修改下，不要common的loadConf，加个配置太麻烦了
class ConfigFileParser:
    @staticmethod
    def _get_option(section, option):
        try:
            cf = ConfigParser()
            cf.read(paths.CONFIG_PATH)
            return cf.get(section=section, option=option)
        except:
            tracebackLogger()
            return ''

    def dict_mode(self):
        return self._get_option('ScanModeHandler','conf.dict_mode')
    def dict_mode_load_dir_dict(self):
        return self._get_option('ScanModeHandler','conf.dict_mode_load_dir_dict')
    def dict_mode_load_mult_dict(self):
        return self._get_option('ScanModeHandler','conf.dict_mode_load_mult_dict')
    
    def fuzz_mode(self):
        return self._get_option('ScanModeHandler','conf.fuzz_mode')
    def fuzz_mode_load_main_dict(self):
        return self._get_option('ScanModeHandler','conf.fuzz_mode_load_main_dict')
    def fuzz_mode_load_ext_dict(self):
        return self._get_option('ScanModeHandler','conf.fuzz_mode_load_ext_dict')

    def request_headers(self):
        return self._get_option('RequestHandler','conf.request_headers')
    def request_header_ua(self):
        return self._get_option('RequestHandler','conf.request_header_ua')
    def request_header_cookie(self):
        return self._get_option('RequestHandler','conf.request_header_cookie')
    def request_header_401_auth(self):
        return self._get_option('RequestHandler','conf.request_header_401_auth')
    def request_timeout(self):
        return self._get_option('RequestHandler','conf.request_timeout')
    def request_delay(self):
        return self._get_option('RequestHandler','conf.request_delay')
    def request_limit(self):
        return self._get_option('RequestHandler','conf.request_limit')
    def request_persistent_connect(self):
        return self._get_option('RequestHandler','conf.request_persistent_connect')
    def request_method(self):
        return self._get_option('RequestHandler','conf.request_method')

    def proxy_server(self):
        return self._get_option('ProxyHandler','conf.proxy_server')

