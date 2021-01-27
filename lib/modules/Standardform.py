#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import difflib
from bs4 import BeautifulSoup
from collections import OrderedDict
from urllib.parse import urljoin
from requests_toolbelt.utils import dump

from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import Requester


class Standardform:
    """
    This module tries to auto-detect standard web authentication forms, and to bruteforce them.
    It is based on several heuristics, and therefore can lead to false positives/negatives.
    It does not handle javascript-based forms or exotic authentication forms.
    """

    def __init__(self, url, verbose=False):
        self.url = url
        self.verbose = verbose
        self.page_html = ''
        self.cookies = dict()
        self.form_number = 0
        self.username_field = None
        self.password_field = None
        self.parameters = None
        self.action_url = None
        self.method = 'POST'
        self.has_csrftoken = False


    def __extract_form_fields(self, soup):
        """
        Turn a BeautifulSoup form into a dict of fields and default values
        """
        fields = OrderedDict()
        for input in soup.find_all('input', attrs={'name': True}):
            if 'type' not in input.attrs:
                input.attrs['type'] = 'text'
            # Single element name/value fields
            if input.attrs['type'].lower() in ('text', 'email', 'hidden', 'password', 'submit', 'image'):
                value = ''
                if 'value' in input.attrs:
                    value = input.attrs['value']
                fields[input.attrs['name']] = value
                continue

            # Checkboxes and radios
            if input.attrs['type'].lower() in ('checkbox', 'radio'):
                value = ''
                if input.has_attr("checked"):
                    if input.has_attr('value'):
                        value = input.attrs['value']
                    else:
                        value = 'on'
                if value:
                    fields[input.attrs['name']] = value
                continue

        # Textareas
        for textarea in soup.find_all('textarea', attrs={'name': True}):
            fields[textarea.attrs['name']] = textarea.string or ''

        # Select fields
        for select in soup.find_all('select', attrs={'name': True}):
            value = ''
            options = select.find_all('option')
            is_multiple = select.has_attr('multiple')
            selected_options = [
                option for option in options
                if option.has_attr('selected') and option.has_attr('value')
            ]

            # If no select options, go with the first one
            if not selected_options and options:
                selected_options = [options[0]]

            if not is_multiple:
                if len(selected_options) == 1:
                    if selected_options[0].has_attr('value'):
                        value = selected_options[0]['value']
                    else:
                        value = ''
            else:
                value = [
                    option['value'] for option in selected_options 
                    if option.has_attr('value')
                ]

            fields[select['name']] = value

        return fields


    def __find_username_field_via_name(self, inputs):
        """
        Try to find the name of username field among a list of input fields.
        Looks for the most evocative value for the "name" attribute
        :param list inputs: List of inputs candidates
        :return str name: Username field name (None if not found)
        """
        for input in inputs:
            for n in ('name', 'login', 'user', 'mail'):
                if n in input.attrs['name'].lower():
                    return input.attrs['name']
        return None


    def check(self):
        r = Requester.get(self.url)

        # Cookie potentially returned are kept to be sent in the auth request
        # because sometimes application might reject request if those cookies are not present
        self.cookies = r.cookies

        # Keep HTML source code of the page for diff calculation in heuristics checks
        # to determine if auth has failed/succeeded
        self.page_html = r.text
        soup = BeautifulSoup(r.text, 'html.parser')

        logger.warning('This module is based on heuristics and is prone to '
            'false negatives/positives')
        

        # Get all <form> on the page
        forms = soup.find_all('form')
        #print(forms)
        if not forms:
            logger.error('No standard web <form> found on the page')
            return False


        # Detect form with password field
        # 1. Check for standard <input type="password" ...> field
        # 2. Otherwise, check for <input type="text" ...> field with evocative name
        target_form = None
        is_input_password_type_text = False
        i = 0
        for f in forms:
            input_password = f.find(
                'input', 
                type=lambda x: x and x.lower()=='password', 
                attrs={'name': True})
            if not input_password:
                input_password = f.find(
                    'input', 
                    type=lambda x: x and x.lower()=='text', 
                    attrs={'name': re.compile('.*(pass|pwd|pswd|pssw|pswrd).*', re.IGNORECASE)})
                if input_password:
                    is_input_password_type_text = True
            if input_password:
                target_form = f
                self.password_field = input_password.attrs['name']
                self.form_number = i
                break
            i += 1

        if target_form:
            logger.info('Standard web authentication <form> seems present on the page')
            logger.info('Detected password field name = {name}'.format(name=self.password_field))
        else:
            logger.error('No standard web auth <form> with password field has been detected '
                'on the page')
            return False


        # Get action url (target) used when submitting form
        if target_form.has_attr('action'):
            form_action = target_form.attrs['action']
            # Absolute URL
            if form_action.lower().startswith('http://') \
               or form_action.lower().startswith('https://'):
                self.action_url = form_action
            # Relative path
            else:
                self.action_url = urljoin(self.url, form_action)
        else:
            self.action_url = r.url
        logger.info('Detected form action URL = {url}'.format(url=self.action_url))


        # Get form method (default POST)
        try:
            self.method = target_form.attrs['method'].upper()
        except:
            self.method = 'POST'


        # Detect username field
        inputs_text = target_form.find_all(
            'input', 
            type=lambda x: x and x.lower() in ('text','email'), 
            attrs={'name': True})
        if is_input_password_type_text:
            try:
                inputs_text.remove(target_form.find(
                    'input', 
                    type=lambda x: x and x.lower()=='text', 
                    attrs={'name': self.password_field}))
            except:
                pass
        if len(inputs_text) == 0:
            self.username_field = None
        elif len(inputs_text) == 1:
            # If only one input field type=text (except password field), take this one
            self.username_field = inputs_text[0].attrs['name']
        else:
            # Take the one with the most explicit name if found, otherwise the first one
            self.username_field = self.__find_username_field_via_name(inputs_text)
            if not self.username_field:
                self.username_field = inputs_text[0].attrs['name']

        # In rare case, username field can have no type
        if not self.username_field:
            inputs_no_type = target_form.find_all(
                'input', 
                type=False, 
                attrs={'name': True})
            self.username_field = self.__find_username_field_via_name(inputs_no_type)         

        if self.username_field:
            logger.info('Detected username field name = {name}'.format(name=self.username_field))
        else:
            logger.info('No username field detected, probably password-only authentication')


        # Heuristic check of anti-CSRF token
        self.has_csrftoken = target_form.find('input', type=lambda x: x and x.lower()=='hidden') is not None
        if self.has_csrftoken:
            logger.info('Heuristic check determines form might have anti-CSRF token')


        # Get ordered list of all form parameters
        self.parameters = self.__extract_form_fields(target_form)
        return True



    def try_auth(self, username, password):

        # If anti-CSRF token might be present, reload the page before every attempt
        # and re-extract form fields
        if self.has_csrftoken:
            r = Requester.get(self.url)
            self.cookies = r.cookies
            soup = BeautifulSoup(r.text, 'html.parser')
            try:
                target_form = soup.find_all('form')[self.form_number]
            except:
                raise AuthException('Problem occured when reloading page. Maybe some WAF/Protection '
                    'is blocking us ?')
            self.parameters = self.__extract_form_fields(target_form)
            if self.password_field not in self.parameters.keys() \
               or (self.username_field and self.username_field not in self.parameters.keys()):
                raise AuthException('Problem occured when reloading page. Maybe some WAF/Protection '
                    'is blocking us ?')


        # Send authentication request
        if self.username_field:
            self.parameters[self.username_field] = username
        self.parameters[self.password_field] = password
        
        if self.method == 'GET':
            r = Requester.get(
                self.action_url, 
                params=self.parameters, 
                cookies=self.cookies)
        else:
            r = Requester.post(
                self.action_url,
                data=self.parameters,
                cookies=self.cookies)
        if self.verbose:
            logger.info('Raw HTTP Request/Response:')
            data = dump.dump_all(r)
            print(data.decode('utf-8'))


        # Check authentication status 
        # HTTP response code check
        if r.status_code >= 400:
            return False

        # Check if response page contains password field
        soup = BeautifulSoup(r.text, 'html.parser')
        input_password = soup.find('input', attrs={'name': self.password_field})
        if input_password:
            return False

        # Heuristic check of failed attemps based on possible error messages
        if re.search('(username\s+or\s+password|cannot\s+log\s*in|unauthorized'
            '|auth(entication)?\s+fail|(invalid|wrong)\s+(cred|user|login|mail|email|e-mail|pass)'
            '|error\s+during\s+(login|auth))', 
            r.text, re.IGNORECASE):
            return False

        # Heuristic check of successful attempt based on page content
        if re.search('(log\s*out|log\s*off|deconn?e|disconn?ec)', r.text, re.IGNORECASE):
            return True

        # Heuristic check of account lockout based on possible error messages
        if re.search('(too\s+many\s+(failed)?\s*(attempt|try|tri)|account\s+(lock|block))', 
            r.text, re.IGNORECASE):
            return False

        # Heuristic check based on source code difference with original page
        s = difflib.SequenceMatcher(None, self.page_html, r.text)
        return (s.quick_ratio() < 0.60)