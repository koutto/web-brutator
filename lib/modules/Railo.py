#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Railo:

    def __init__(self, url):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.http_auth_type = None


    def check(self):

        # Server Administration
        r = Requester.get('{}/railo-context/admin/server.cfm'.format(self.url))
        if r.status_code == 200 and 'type="password"' in r.text:
            self.interface = 'railo-server-admin'
            self.interface_url = '{}/railo-context/admin/server.cfm'.format(self.url)
            logger.info('Railo Server administration console detected: {}'.format(
                self.interface_url))
            return True

        # Web Administration
        r = Requester.get('{}/railo-context/admin/web.cfm'.format(self.url))
        if r.status_code == 200 and 'type="password"' in r.text:
            self.interface = 'railo-server-admin'
            self.interface_url = '{}/railo-context/admin/web.cfm'.format(self.url)
            logger.info('Railo Web administration console detected: {}'.format(
                self.interface_url))
            return True

        logger.error('No Railo authentication interface detected')
        return False


    def try_auth(self, username, password):

        # Note: In Railo, there is no username

        data = OrderedDict([ 
            ("lang", "en"),
            ("rememberMe", "yyyy"),
            ("submit", "submit")
        ])

        if self.interface == 'railo-server-admin':
            data['login_passwordserver'] = password
            r = Requester.post(self.interface_url, data)
            return ('login.login_password' not in r.text)

        elif self.interface == 'railo-web-admin':
            data['login_passwordweb'] = password
            r = Requester.post(self.interface_url, data)
            return ('login.login_password' not in r.text)

        else:
            raise AuthException('No auth interface found during initialization')            