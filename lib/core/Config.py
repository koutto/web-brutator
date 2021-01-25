#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

VERSION = '0.2'
BANNER = """
 __      __      ___.            __________                __          __                
/  \    /  \ ____\_ |__          \______   \_______ __ ___/  |______ _/  |_  ___________ 
\   \/\/   // __ \| __ \   ______ |    |  _/\_  __ \  |  \   __\__  \   __\ /  _ \_  _ _\\
 \        /\  ___/| \_\ \ /_____/ |    |   \ |  | \/  |  /|  |  / __ \|  | (  <_> )  | \/
  \__/\  /  \___  >___  /         |______  / |__|  |____/ |__| (____  /__|  \____/|__|   
       \/       \/    \/                 \/                         \/                   
                                                                        Version {}
""".format(VERSION)


BASEPATH = os.path.dirname(os.path.realpath(__file__+'/../..'))
DEFAULT_NB_THREADS = 10
MAX_THREADS = 50
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'
TIMEOUT = 20
MAX_ERRORS = 10

