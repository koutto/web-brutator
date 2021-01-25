#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import threading
import urllib3
import requests
import sys
import traceback

from lib.core.Bruteforcer import Bruteforcer
from lib.core.Config import *
from lib.core.Exceptions import RequestException
from lib.core.Logger import logger
from lib.core.Output import Output
from lib.core.Requester import Requester
from lib.core.Utils import Utils
from lib.core.Wordlist import Wordlist

urllib3.disable_warnings()


class Controller:

    def __init__(self, args):
        self.args = args
        self.mutex = threading.Lock()
        self.creds_found = []
        self.output = Output()
        self.consec_reqexcept = 0

    def run(self):

        # List supported modules 
        if self.args.list:
            print('List of supported modules:')
            for mod in Utils.list_modules():
                print('- {}'.format(mod))
            return

        # Check if target is available
        logger.info('Check if target {url} is reachable...'.format(url=self.args.url))
        try:
            r = Requester.get(self.args.url)
        except RequestException as e:
            logger.error('Target URL seems not reachable:')
            logger.error(e)
            sys.exit(0)
        logger.success('Connection to target OK. HTTP Status {}'.format(r.status_code))

        # Handle potential <meta> refresh
        meta_refresh_url = Requester.get_meta_redirect_url(r.text, self.args.url)
        if meta_refresh_url:
            logger.info('Meta refresh mechanism has been detected. Following redirect...')
            self.args.url = meta_refresh_url
            try:
                r = Requester.get(self.args.url)
            except RequestException as e:
                logger.error('Redirected URL seems not reachable:')
                logger.error(e)
                sys.exit(0)
            logger.success('Connection to redirection OK. HTTP Status {}'.format(r.status_code))            

        # Create wordlist queue
        try:
            self.wordlist = Wordlist(self.args.username,
                                self.args.userlist,
                                self.args.password,
                                self.args.passlist,
                                self.args.combolist) 
            logger.info('Number of creds that will be tested: {}'.format(
                self.wordlist.length))
        except Exception as e:
            logger.error(e)
            sys.exit(0)

        # Initialize module
        try:
            mod = importlib.import_module('lib.modules.{}'.format(
                self.args.type.capitalize()))
        except Exception as e:
            logger.error('Error while importing module lib.modules.{}'.format(
                self.args.type.capitalize()))
            traceback.print_exc()
            return
        module = getattr(mod, self.args.type.capitalize())(
            self.args.url, verbose=self.args.verbose)

        # Detect authentication interface
        try:
            if not module.check():
                return
        except RequestException as e:
            logger.warning(e)

        # Run bruteforce
        self.run_bruteforcer(module)
        self.output.newline('')

        logger.info('Bruteforce finished !')
        if self.args.verbose:
            if len(self.creds_found) > 0:
                logger.success('{} valid credentials found:'.format(
                    len(self.creds_found)))
                for username, password in self.creds_found:
                    logger.success('{}:{}'.format(username, password))
            else:
                logger.error('No valid credentials found :\'(')


    def run_bruteforcer(self, module):
        self.bruteforcer = Bruteforcer(module, 
                                       self.wordlist,
                                       self.success_creds_callback,
                                       self.wrong_creds_callback,
                                       self.fatal_error_callback,
                                       self.request_error_callback,
                                       threads=self.args.threads) 
        # try:
        # TODO: handle exception !!
        logger.info('Starting bruteforce with {} threads...'.format(
            self.bruteforcer.nb_threads))
        self.bruteforcer.start()
        while True:
            try:
                while not self.bruteforcer.wait(0.3):
                    continue
                break

            except (KeyboardInterrupt, SystemExit) as e:
                self.handle_interrupt()
        # except


    def success_creds_callback(self, username, password, index):
        with self.mutex:
            self.consec_reqexcept = 0
            self.creds_found.append((username, password))
            self.output.last_creds(username, password, index, 
                self.wordlist.length, verbose=self.args.verbose)
            self.output.found_creds(self.args.type, username, password)
            if self.args.stoponsuccess:
                self.bruteforcer.stop()


    def wrong_creds_callback(self, username, password, index):
        with self.mutex:
            self.consec_reqexcept = 0
            self.output.last_creds(username, password, index, 
                self.wordlist.length, verbose=self.args.verbose)


    def fatal_error_callback(self, message):
        with self.mutex:
            self.output.fatal_error('Fatal error: {}'.format(message))


    def request_error_callback(self, message):
        with self.mutex:
            self.consec_reqexcept += 1
            self.output.warning(message)
            if self.consec_reqexcept >= self.args.max_errors:
                self.output.fatal_error('Too many consecutive network requests ' \
                    'exceptions. Quitting !')
                self.bruteforcer.stop()
                sys.exit(0)


    def handle_interrupt(self):
        self.output.warning('CTRL+C detected: Pausing threads, please wait...')
        self.bruteforcer.pause()

        while True:
            msg = "[e]xit / [c]ontinue"
            self.output.inline(msg + ': ')

            option = input()

            if option.lower() == 'e':
                self.exit = True
                self.bruteforcer.stop()
                sys.exit(0)

            elif option.lower() == 'c':
                self.bruteforcer.play()
                return

            else:
                continue