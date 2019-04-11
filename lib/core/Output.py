#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import colored
import sys
import threading


class Output:

    def __init__(self):
        self.mutex = threading.Lock()
        self.last_inline = False


    def inline(self, string):
        self.erase()
        sys.stdout.write(string)
        sys.stdout.flush()
        self.last_inline = True


    def erase(self):
        sys.stdout.write('\033[1K')
        sys.stdout.write('\033[0G')


    def newline(self, string):
        if self.last_inline == True:
            self.erase()
        sys.stdout.write(string + '\n')

        sys.stdout.flush()
        self.last_inline = False
        sys.stdout.flush()


    def last_creds(self, username, password, index, length, verbose=False):
        with self.mutex:
            percentage = lambda x, y: float(x) / float(y) * 100

            message = '{percent:.2f}% - {index}/{length} - '.format(
                percent=percentage(index, length),
                index=index, length=length)
            message += 'Testing: {}:{}'.format(username, password)
            if verbose:
                self.newline(message)
            else:
                self.inline(message)


    def found_creds(self, username, password):
        with self.mutex:
            message = 'Found creds: {}:{}'.format(username, password)
            message = colored.stylize(message, colored.fg('light_green') + colored.attr('bold'))
            if self.last_inline == True:
                self.erase()
            print(message)


    def error(self, message):
        with self.mutex:
            text = colored.stylize(message, 
                colored.fg('red') + colored.attr('bold'))
            if self.last_inline == True:
                self.erase()
            print(text)


    def fatal_error(self, message):
        with self.mutex:
            text = colored.stylize(message, 
                colored.fg('white') + colored.bg('red') + colored.attr('bold'))
            if self.last_inline == True:
                self.erase()
            print(text)        


    def warning(self, message):
        with self.mutex:
            text = colored.stylize(message, 
                colored.fg('yellow') + colored.attr('bold'))
            if self.last_inline == True:
                self.erase()
            print(text)            
