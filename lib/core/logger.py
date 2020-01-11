#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import traceback
import logging

logger = logging.getLogger("logger")
handler = logging.FileHandler(filename="LalalaScan.log")
logger.setLevel(logging.DEBUG)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def tracebackLogger():
    logger.debug(traceback.format_exc())