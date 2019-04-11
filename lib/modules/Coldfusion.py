#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import hmac
import re
from collections import OrderedDict

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Coldfusion:

    def __init__(self, url):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.http_auth_type = None


    def check(self):

        r = Requester.get('{}/CFIDE/administrator/enter.cfm'.format(self.url))
        if r.status_code == 200 and 'type="password"' in r.text.lower():
            self.interface_url = '{}/CFIDE/administrator/enter.cfm'.format(self.url)

            # Version 6
            if 'name="cfadminPassword"' in r.text \
                    and 'name="requestedURL"' in r.text \
                    and 'name="cfadminUserId"' not in r.text \
                    and 'name="salt"' not in r.text:
                self.interface = 'coldfusion-6-admin'
                logger.info('Coldfusion 6 administration console detected: {}'.format(
                    self.interface_url))
                return True

            # Versions 7/8/9
            elif 'name="cfadminPassword"' in r.text \
                    and 'name="requestedURL"' in r.text \
                    and 'name="cfadminUserId"' in r.text \
                    and 'name="salt"' in r.text:
                self.interface = 'coldfusion-7-8-9-admin'
                logger.info('Coldfusion 7/8/9 administration console detected: {}'.format(
                    self.interface_url))
                return True

            # Versions 10/11
            elif 'name="cfadminPassword"' in r.text \
                    and 'name="requestedURL"' in r.text \
                    and 'name="cfadminUserId"' in r.text \
                    and 'name="salt"' not in r.text:
                self.interface = 'coldfusion-10-11-admin'
                logger.info('Coldfusion 10/11 administration console detected: {}'.format(
                    self.interface_url))
                return True

        r = Requester.get('{}/CFIDE/administrator/index.cfm'.format(self.url))
        if r.status_code == 200 and 'type="password"' in r.text.lower():
            self.interface_url = '{}/CFIDE/administrator/index.cfm'.format(self.url)    
            
            # Version 5
            if 'name="PasswordProvided_required"' in r.text \
                    and 'name="PasswordProvided"' in r.text:
                self.interface = 'coldfusion-5-admin'
                logger.info('Coldfusion 5 administration console detected: {}'.format(
                    self.interface_url))
                return True

        logger.error('No Coldfusion authentication interface detected')
        return False


    def try_auth(self, username, password):

        if self.interface == 'coldfusion-5-admin':
            data = {
                'PasswordProvided_required': 'You+must+provide+a+password.',
                'PasswordProvided' : password,
                'Submit' : 'Password',
            }
            r = Requester.post(self.interface_url, data)
            return (r.status_code == 200 and 'name="PasswordProvided"' not in r.text)

        elif self.interface == 'coldfusion-6-admin':
            data = {
                'cfadminPassword': password,
                'requestedURL': '/CFIDE/administrator/index.cfm',
                'submit': 'Login',
            }
            r = Requester.post(self.interface_url, data)
            return (r.status_code == 200 and 'name="cfadminPassword"' not in r.text)

        elif self.interface == 'coldfusion-7-8-9-admin':
            salt = self._get_salt(self.interface_url)
            hash_ = hmac.new(bytes(salt, 'ascii'), 
                             bytes(hashlib.sha1(password.encode('utf-8')).hexdigest().upper(), 'ascii'), 
                             hashlib.sha1).hexdigest().upper()
            data = {
                'cfadminPassword' : hash_,
                'requestedURL' : '/CFIDE/administrator/enter.cfm?',
                'cfadminUserId' : username,
                'salt' : salt,
                'submit' : 'Login',
            }
            r = Requester.post(self.interface_url, data)
            return (r.status_code == 200 and 'name="cfadminPassword"' not in r.text)

        elif self.interface == 'coldfusion-10-11-admin':
            hash_ = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            data = {
                'cfadminPassword' : hash_,
                'requestedURL' : '/CFIDE/administrator/enter.cfm?',
                'cfadminUserId' : username,
                'submit' : 'Login',
            }
            r = Requester.post(self.interface_url, data)
            return (r.status_code == 200 and 'name="cfadminPassword"' not in r.text)


    def _get_salt(self, url):
        r = Requester.get(url)
        m = re.search('<input name="salt" type="hidden" value="(?P<salt>\S+?)">',
            r.text)
        if not m:
            raise RequestException('Unable to retrieve salt from {}'.format(url))
        else:          
            return m.group('salt')