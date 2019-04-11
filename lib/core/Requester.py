#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import enum
import requests
import requests_ntlm

from lib.core.ArgumentsParser import *
from lib.core.Config import *
from lib.core.Exceptions import RequestException
import lib.core.Globals as Globals


class AuthMode(enum.Enum):
    BASIC   = enum.auto()
    DIGEST  = enum.auto()
    NTLM    = enum.auto()
    UNKNOWN = enum.auto()


class Requester:

    @staticmethod
    def get(url, headers={}, allow_redirects=True):
        headers['User-Agent'] = USER_AGENT
        try:
            r = requests.get(url, headers=headers, 
                verify=False, timeout=Globals.timeout, 
                allow_redirects=allow_redirects)
            return r
        except Exception as e:
            raise RequestException('Network error: {}'.format(e))


    @staticmethod
    def post(url, data, headers={}, allow_redirects=True):
        headers['User-Agent'] = USER_AGENT
        try:
            r = requests.post(url, data=data, 
                verify=False, headers=headers, timeout=Globals.timeout,
                allow_redirects=allow_redirects)
            return r
        except Exception as e:
            raise RequestException('Network error: {}'.format(e))


    @staticmethod
    def get_http_auth_type(url, headers={}):
        headers['User-Agent'] = USER_AGENT
        try:
            r = requests.get(url, verify=False, headers=headers, 
                timeout=Globals.timeout)
        except Exception as e:
            raise RequestException('Network error: {}'.format(e))

        if r.status_code == 401:
            respheader = r.headers['WWW-Authenticate'].lower()
            if 'basic' in respheader:
                return AuthMode.BASIC
            elif 'digest' in respheader:
                return AuthMode.DIGEST
            elif 'ntlm' in respheader:
                return AuthMode.NTLM
            else:
                return AuthMode.UNKNOWN
        else:
            return AuthMode.UNKNOWN


    @staticmethod
    def http_auth(url, auth_type, username, password, headers={}):
        if auth_type == AuthMode.BASIC:
            auth = requests.auth.HTTPBasicAuth(username, password)
        elif auth_type == AuthMode.DIGEST:
            auth = requests.auth.HTTPDigestAuth(username, password)
        elif auth_type == AuthMode.NTLM:
            auth = requests_ntlm.HttpNtlmAuth(username, password)
        else:
            return None

        headers['User-Agent'] = USER_AGENT
        try:
            r = requests.get(url, headers=headers, auth=auth, 
                    verify=False, timeout=Globals.timeout)
            return r
        except Exception as e:
            raise RequestException('Network error: {}'.format(e))


