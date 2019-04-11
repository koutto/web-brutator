#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import queue
import threading


class Wordlist:

    def __init__(self, 
                 username=None, 
                 userfile=None, 
                 password=None, 
                 passfile=None, 
                 combofile=None):
        self.queue = queue.Queue()
        self.mutex = threading.Lock()
        self.index = 0
        self.length = 0

        if username is not None:
            if password is not None:
                self.queue.put((username, password))
            elif passfile is not None:
                with open(passfile, 'r') as f:
                    for p in f:
                        self.queue.put((username, p.rstrip()))
            else:
                raise Exception('Unexpected error while building wordlist queue')

        elif userfile is not None:
            with open(userfile, 'r') as fu:
                for u in fu:
                    if password is not None:
                        self.queue.put((u.rstrip(), password))
                    elif passfile is not None:
                        with open(passfile, 'r') as fp:
                            for p in fp:
                                self.queue.put((u.rstrip(), p.rstrip()))
                    else:
                        raise Exception('Unexpected error while building wordlist queue')

        elif combofile is not None:
            with open(combofile, 'r') as f:
                for c in f:
                    if ':' not in c:
                        continue
                    u, p = c.split(':', maxsplit=1)
                    self.queue.put((u.rstrip(), p.rstrip()))

        else:
            raise Exception('Unexpected error while building wordlist queue')

        self.length = self.queue.qsize()


    def increment_index(self):
        with self.mutex:
            self.index += 1
        return


    def decrement_index(self):
        with self.mutex:
            self.index -= 1
        return



