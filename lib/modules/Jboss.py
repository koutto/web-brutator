#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Jboss:

    def __init__(self, url):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.http_auth_type = None


    def check(self):

        # Interface 1: admin-console
        r = Requester.get('{}/admin-console/login.seam'.format(self.url))
        if r.status_code == 200:
            self.interface = 'admin-console'
            self.interface_url = '{}/admin-console/login.seam'.format(self.url)
            logger.info('Jboss authentication interface detected: {}'.format(
                self.interface_url))
            return True

        # Interface 2: jmx-console
        auth_type = Requester.get_http_auth_type('{}/jmx-console/'.format(self.url))
        if auth_type is not AuthMode.UNKNOWN:
            self.interface = 'jmx-console'
            self.interface_url = '{}/jmx-console/'.format(self.url)
            self.http_auth_type = auth_type
            logger.info('Jboss jmx-console interface detected: {}'.format(
                self.interface_url))
            return True

        # Interface 3: web-console
        auth_type = Requester.get_http_auth_type('{}/web-console/'.format(self.url))
        if auth_type is not AuthMode.UNKNOWN:
            self.interface = 'web-console'
            self.interface_url = '{}/web-console/'.format(self.url)
            self.http_auth_type = auth_type
            logger.info('Jboss web-console interface detected: {}'.format(
                self.interface_url))
            return True

        # Interface 4: management
        auth_type = Requester.get_http_auth_type('{}/management/'.format(self.url))
        if auth_type is not AuthMode.UNKNOWN:
            self.interface = 'management'
            self.interface_url = '{}/management/'.format(self.url)
            self.http_auth_type = auth_type
            logger.info('Jboss management interface detected: {}'.format(
                self.interface_url))
            return True

        # Interface 5: management 2
        r = Requester.get('{}/console'.format(self.url))
        if r.status_code == 200:
            tmp = r.url[:r.url.rindex('/')]
            self.interface_url = '{0}/management'.format(tmp[:tmp.rindex('/')])
            auth_type = Requester.get_http_auth_type(self.interface_url)
            if auth_type is not AuthMode.UNKNOWN:
                self.interface = 'management'
                self.http_auth_type = auth_type
                logger.info('Jboss management interface detected: {}'.format(
                    self.interface_url))
                return True        

        logger.error('No Jboss authentication interface detected')
        return False


    def try_auth(self, username, password):
        if self.interface == 'admin-console':
            # We need to retrieve ViewState value
            r = Requester.get(self.interface_url)
            m = re.search('<input type="hidden" name="javax\.faces\.ViewState" ' \
                'id="javax\.faces\.ViewState" value="(?P<viewstate>.*?)"', r.text)
            if not m:
                raise RequestException('Unable to retrieve ViewState from {}'.format(self.interface_url))

            data = OrderedDict([
                ("login_form", "login_form"),
                ("login_form:name", username),
                ("login_form:password", password),
                ("login_form:submit", "Login"),
                ("javax.faces.ViewState", m.group('viewstate')),
            ])
            # We also need to retrieve JSESSIONID value
            m = re.search(r'JSESSIONID=(?P<jsessionid>.*); Path=\/admin-console', 
                r.headers['Set-Cookie'])
            if not m:
                raise RequestException('Unable to retrieve JSESSIONID value ' \
                    'from {}'.format(self.interface_url))

            r = Requester.post(self.interface_url, data, 
                headers={'Cookie': 'JSESSIONID={}'.format(m.group('jsessionid'))},
                allow_redirects=False)

            status = ('name="login_form:password"' not in r.text \
                and 'Not logged in' not in r.text)
            return status

        elif self.interface == 'jmx-console':
            r = Requester.http_auth(self.interface_url, self.http_auth_type, 
                username, password)
            return (r.status_code != 401)

        elif self.interface == 'management':
            r = Requester.http_auth(self.interface_url, self.http_auth_type, 
                username, password)
            return (r.status_code != 401) 

        elif self.interface == 'web-console':
            r = Requester.http_auth(self.interface_url, self.http_auth_type, 
                username, password)
            return (r.status_code != 401) 

        else:
            raise AuthException('No auth interface found during initialization')            