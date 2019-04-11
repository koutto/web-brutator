#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Weblogic:

    def __init__(self, url):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.http_auth_type = None


    def check(self):

        r = Requester.get('{}/console/j_security_check'.format(self.url))
        if 'name="j_password"' in r.text:
            self.interface = 'weblogic-admin'
            self.interface_url = '{}/console/j_security_check'.format(self.url)
            logger.info('Weblogic administration console detected: {}'.format(
                self.interface_url))
            logger.warning('Warning: By default, Weblogic has an account lockout ' \
                'feature (max 5 failures per 5 minutes, lockout duration of 30min)')
            return True

        logger.error('No Weblogic authentication interface detected')
        return False


    def try_auth(self, username, password):
        if self.interface == 'weblogic-admin':
            data = { 
                'j_username': username,
                'j_password': password,
                'j_character_encoding': 'UTF-8',
            }
            r = Requester.post(self.interface_url, data)
            return ('name="j_password"' not in r.text)

        else:
            raise AuthException('No auth interface found during initialization')            