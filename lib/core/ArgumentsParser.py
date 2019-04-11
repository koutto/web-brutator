#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import re

from lib.core.Config import *
from lib.core.Utils import Utils, LineWrapRawTextHelpFormatter
import lib.core.Globals as Globals

class ArgumentsParser:

    formatter_class = lambda prog: LineWrapRawTextHelpFormatter(
        prog, max_help_position=100)

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            formatter_class=ArgumentsParser.formatter_class)
        self.parser.add_argument('--url', 
            type=self.check_arg_url, dest='url', help='Target URL')
        self.parser.add_argument('--target', 
            type=self.check_arg_type, dest='type', help='Target type')
        self.parser.add_argument('-u', '--username', 
            type=str, dest='username', help='Single username')
        self.parser.add_argument('-U', '--userlist', 
            type=self.check_arg_file, dest='userlist', help='Usernames list')
        self.parser.add_argument('-p', '--password',
            type=str, dest='password', help='Single password')
        self.parser.add_argument('-P', '--passlist',
            type=self.check_arg_file, dest='passlist', help='Passwords list')
        self.parser.add_argument('-C', '--combolist',
            type=self.check_arg_file, dest='combolist', help='Combos username:password list')
        self.parser.add_argument('-t', '--threads',
            type=self.check_arg_threads, dest='threads', default=DEFAULT_NB_THREADS, 
            help='Number of threads [1-50] (default: {})'.format(DEFAULT_NB_THREADS))
        self.parser.add_argument('-s', '--stoponsuccess',
            action='store_true', dest='stoponsuccess', default=False, help='Stop on success')
        self.parser.add_argument('-v', '--verbose',
            action='store_true', dest='verbose', default=False, help='Print every tested creds')
        self.parser.add_argument('-e', '--max-errors',
            type=int, dest='max_errors', default=MAX_ERRORS, 
            help='Number of accepted consecutive errors (default: {})'.format(MAX_ERRORS))
        self.parser.add_argument('--timeout',
            type=int, dest='timeout', default=TIMEOUT, 
            help='Time limit on the response (default: {}s)'.format(TIMEOUT))
        self.parser.add_argument('-l', '--list-modules',
            action='store_true', dest='list', default=False, help='Display list of modules')

        self.args = self.parser.parse_args()
        self.check_args()


    def check_arg_url(self, url):
        url = str(url)
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not regex.match(url):
            raise argparse.ArgumentTypeError('Invalid URL submitted')
        # Add http:// prefix if necessary
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://{0}'.format(url)
        # Remove potential ending slash at end of URL
        while url.endswith('/'):
            url = url[:-1]
        return url


    def check_arg_type(self, type_):
        type_ = str(type_).lower()
        if type_ not in Utils.list_modules():
            raise argparse.ArgumentTypeError('Target type not supported')
        return type_


    def check_arg_file(self, file):
        file = str(file)
        if not os.path.isfile(file):
            raise argparse.ArgumentTypeError('Path "{}" is not a file'.format(file))
        return os.path.abspath(file)


    def check_arg_threads(self, threads):
        try:
            threads = int(threads)
        except:
            raise argparse.ArgumentTypeError('Number of threads must be an integer')
        if threads < 1 or threads > MAX_THREADS:
            raise argparse.ArgumentTypeError('Number of threads must be <= {}'.format(
                MAX_THREADS))
        return threads


    def check_args(self):
        if self.args.list is False:
            if self.args.url is None:
                self.parser.error('Target URL is required (--url)')
            if self.args.type is None:
                self.parser.error('Target type is required (--target)')

            if self.args.username is not None and self.args.userlist is not None:
                self.parser.error('Both -u and -U cannot be used at the same time')

            if self.args.password is not None and self.args.passlist is not None:
                self.parser.error('Both -p and -P cannot be used at the same time')

            if self.args.combolist is not None:
                if self.args.username is not None \
                        or self.args.userlist is not None \
                        or self.args.password is not None \
                        or self.args.passlist is not None:
                    self.parser.error('When combolist is used, -u, -U, -p and -P ' \
                        'are not supported')

            if self.args.username is None \
                    and self.args.userlist is None \
                    and self.args.password is None \
                    and self.args.passlist is None \
                    and self.args.combolist is None:
                self.parser.error('Username/userlist + password/passlist or ' \
                    'combolist required')

        Globals.timeout = self.args.timeout

        return