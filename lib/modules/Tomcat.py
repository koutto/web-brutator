#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Tomcat:

    def __init__(self, url, verbose=False):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.http_auth_type = None


    def check(self):

        auth_type = Requester.get_http_auth_type('{}/manager/html'.format(self.url))
        if auth_type is not AuthMode.UNKNOWN:
            self.interface = 'tomcat-manager'
            self.interface_url = '{}/manager/html'.format(self.url)
            self.http_auth_type = auth_type
            logger.info('Tomcat Manager interface detected: {}'.format(
                self.interface_url))
            logger.warning('Warning: By default, Tomcat has an account lockout ' \
                'feature (max 5 failures, lockout duration of 300s)')
            return True

        logger.error('No Tomcat authentication interface detected')
        return False


    def try_auth(self, username, password):
        if self.interface == 'tomcat-manager':
            r = Requester.http_auth(self.interface_url, self.http_auth_type, 
                username, password)
            return (r.status_code != 401)

        else:
            raise AuthException('No auth interface found during initialization')            