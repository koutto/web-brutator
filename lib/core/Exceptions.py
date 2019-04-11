#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# An AuthException will stop the bruteforcing (unexpected error)
class AuthException(Exception):
    pass

# A RequestException might be due to network congestion and will 
# stop bruteforcing only after several consecutive similar exceptions
class RequestException(Exception):
    pass