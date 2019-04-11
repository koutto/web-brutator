#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading

from lib.core.Exceptions import AuthException, RequestException


class Bruteforcer:

    def __init__(self, 
                 auth_module,
                 wordlist,
                 success_creds_callback,
                 wrong_creds_callback,
                 fatal_error_callback,
                 request_error_callback,
                 threads=1):

        self.auth_module = auth_module
        self.wordlist = wordlist
        self.success_creds_callback = success_creds_callback
        self.wrong_creds_callback = wrong_creds_callback
        self.fatal_error_callback = fatal_error_callback
        self.request_error_callback = request_error_callback
        self.nb_threads = threads if wordlist.length >= threads else wordlist.length
        self.threads = []
        self.running = False
        self.creds_found = []


    def wait(self, timeout=None):
        for thread in self.threads:
            thread.join(timeout)

            if timeout is not None and thread.is_alive():
                return False

        return True    


    def setup_threads(self):
        if len(self.threads) != 0:
            self.threads = []

        for thread in range(self.nb_threads):
            new_thread = threading.Thread(target=self.thread_proc)
            new_thread.daemon = True
            self.threads.append(new_thread)


    def start(self):
        # Setting up testers

        # Setting up threads
        self.setup_threads()
        self.nb_running_threads = len(self.threads)
        self.running = True
        self.play_event = threading.Event()
        self.paused_semaphore = threading.Semaphore(0)
        self.play_event.clear()
        self.exit = False

        for thread in self.threads:
            thread.start()

        self.play()


    def play(self):
        self.play_event.set()


    def pause(self):
        self.play_event.clear()
        for thread in self.threads:
            if thread.is_alive():
                self.paused_semaphore.acquire()


    def stop(self):
        self.running = False
        self.play()


    def is_running(self):
        return self.running


    def finish_threads(self):
        self.running = False
        # self.finishedEvent.set()        


    def is_finished(self):
        return self.nb_running_threads == 0


    def stop_thread(self):
        self.nb_running_threads -= 1


    def check_auth(self, username, password):
        return self.auth_module.try_auth(username, password)


    def thread_proc(self):
        self.play_event.wait()
        try:
            while not self.wordlist.queue.empty():
                username, password = self.wordlist.queue.get()
                self.wordlist.increment_index()
                try:
                    status = self.check_auth(username, password)

                    if status is True:
                        self.creds_found.append((username, password))
                        self.success_creds_callback(username, password, 
                            self.wordlist.index)
                    else:
                        self.wrong_creds_callback(username, password,
                            self.wordlist.index)

                except AuthException as e:
                    self.fatal_error_callback(e)
                    continue

                except RequestException as e:
                    self.request_error_callback(e)
                    # Retry the creds
                    self.wordlist.queue.put((username, password))
                    self.wordlist.decrement_index()

                finally:
                    if not self.play_event.isSet():
                        self.paused_semaphore.release()
                        self.play_event.wait()

                    if not self.running:
                        break

        finally:
            self.stop_thread()


