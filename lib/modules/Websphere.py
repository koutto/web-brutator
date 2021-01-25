#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Websphere:

    def __init__(self, url, verbose=False):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.action_url = None
        self.http_auth_type = None


    def check(self):

        r = Requester.get('{}/ibm/console/logon.jsp'.format(self.url))
        if 'name="j_password"' in r.text:
            self.interface = 'websphere-admin'
            self.interface_url = '{}/ibm/console/logon.jsp'.format(self.url)
            self.action_url = '{}/ibm/console/j_security_check'.format(self.url)
            logger.info('Websphere administration console detected: {}'.format(
                self.interface_url))
            return True

        logger.error('No Websphere authentication interface detected')
        return False


    def try_auth(self, username, password):
        if self.interface == 'websphere-admin':
            data = { 
                'j_username': username,
                'j_password': password,
                'action': 'Go',
            }
            r = Requester.post(self.action_url, data)
            return ('name="j_password"' not in r.text)

        else:
            raise AuthException('No auth interface found during initialization')            