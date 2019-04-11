#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Axis2:

    def __init__(self, url):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.http_auth_type = None


    def check(self):

        r = Requester.get('{}/axis2/axis2-admin/login'.format(self.url))
        if r.status_code == 200 and 'name="password"' in r.text:
            self.interface = 'axis2-admin'
            self.interface_url = '{}/axis2/axis2-admin/login'.format(self.url)
            logger.info('Axis2 administration console detected: {}'.format(
                self.interface_url))
            return True

        logger.error('No Axis2 authentication interface detected')
        return False


    def try_auth(self, username, password):
        if self.interface == 'axis2-admin':
            data = {
                'userName': username,
                'password': password,
                'submit': '+Login+',
            }
            r = Requester.post(self.interface_url, data)
            return (r.status_code == 200 and 'name="password"' not in r.text)

        else:
            raise AuthException('No auth interface found during initialization')            