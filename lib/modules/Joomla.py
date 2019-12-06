#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Joomla:

    def __init__(self, url):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.http_auth_type = None
        self.token = None
        self.cookie = None
        self.option = None


    def check(self):

        r = Requester.get('{}/administrator/index.php'.format(self.url))
        #print(r.headers)
        if 'form action="/administrator/index.php"' in r.text:
            self.interface = 'joomla-admin'
            self.interface_url = '{}/administrator/index.php'.format(self.url)
            logger.info('Joomla administration page detected: {}'.format(
                self.interface_url))

            # Extract session cookie
            try:
                self.cookie = r.headers['Set-Cookie'].split(';')[0]
                logger.info('Extracted session cookie: {}'.format(self.cookie))
            except:
                logger.error('Unable to extract session cookie')
                return False

            # Extract token
            m = re.search('type="hidden" name="(.*)" value="1"', r.text)
            try:
                self.token = m.group(1)
                logger.info('Extracted token value: {}'.format(self.token))
            except:
                logger.error('Unable to extract token from page !')
                return False

            # Extract option
            m = re.search('type="hidden" name="option" value="(.*)"', r.text)
            try:
                self.option = m.group(1)
            except:
                # Default option value
                self.option = 'com_login'

            return True

        logger.error('No Joomla administration interface detected')
        return False


    def try_auth(self, username, password):
        if self.interface == 'joomla-admin':
            r = Requester.get(self.interface_url)

            data = {
                'username': username,
                'passwd': password,
                #'lang': 'en-GB',
                'option': self.option,
                'task': 'login',
                self.token: '1',
            }
            r = Requester.post(
                self.interface_url, 
                data,
                headers={
                    'Cookie': self.cookie,
                })

            if 'input name="passwd"' not in r.text:
                self.cookie = 'a=a'
                return True
            else:
                return False

        else:
            raise AuthException('No auth interface found during intialization')
