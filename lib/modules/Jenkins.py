#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Jenkins:

    def __init__(self, url):
        self.url = url
        self.interface = None
        self.interface_url = None
        self.action_url = None
        self.http_auth_type = None

    def check(self):
        """
        <form method="post" name="login" action="j_acegi_security_check" style="text-size:smaller">
        <table><tr><td>User:</td><td><input type="text" name="j_username" id="j_username" autocorrect="off" autocapitalize="off" />
        </td></tr><tr><td>Password:</td><td><input type="password" name="j_password" /></td></tr><tr><td align="right">
        <input id="remember_me" type="checkbox" name="remember_me" /></td><td><label for="remember_me">Remember me on this computer</label>
        </td></tr></table><input name="from" type="hidden" value="/" />
        <input name="Submit" type="submit" value="log in" class="submit-button primary" /><script>
        $('j_username').focus();
        </script></form>
        """
        r = Requester.get('{}/login'.format(self.url))
        if r.status_code == 200 and 'name="j_password"' in r.text:
            self.interface = 'jenkins-admin'
            self.interface_url = '{}/login'.format(self.url)
            self.action_url = '{}/j_acegi_security_check'.format(self.url)
            logger.info('Jenkins administration console detected: {}'.format(
                self.interface_url))
            return True

        logger.error('No Jenkins authentication interface detected')
        return False


    def try_auth(self, username, password):
        if self.interface == 'jenkins-admin':
            data = {
                'j_username': username,
                'j_password': password,
                'Submit': 'Sign+in',
            }
            r = Requester.post(self.action_url, data)
            return ('name="j_password"' not in r.text)

        else:
            raise AuthException('No auth interface found during initialization')            