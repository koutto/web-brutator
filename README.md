# Web Brutator

Fast Modular Web Interfaces Bruteforcer

# :inbox_tray: Install
```
python3 -m pip install -r requirements.txt
```

# :fast_forward: Usage
```
$ python3 web-brutator.py -h

 __      __      ___.            __________                __          __                
/  \    /  \ ____\_ |__          \______   \_______ __ ___/  |______ _/  |_  ___________ 
\   \/\/   // __ \| __ \   ______ |    |  _/\_  __ \  |  \   __\__  \   __\ /  _ \_  _ _\
 \        /\  ___/| \_\ \ /_____/ |    |   \ |  | \/  |  /|  |  / __ \|  | (  <_> )  | \/
  \__/\  /  \___  >___  /         |______  / |__|  |____/ |__| (____  /__|  \____/|__|   
       \/       \/    \/                 \/                         \/                   
                                                                        Version 0.2

usage: web-brutator.py [-h] [--url URL] [--target TYPE] [-u USERNAME]
                       [-U USERLIST] [-p PASSWORD] [-P PASSLIST]
                       [-C COMBOLIST] [-t THREADS] [-s] [-v] [-e MAX_ERRORS]
                       [--timeout TIMEOUT] [-l]

optional arguments:
  -h, --help                   show this help message and exit
  --url URL                    Target URL
  --target TYPE                Target type
  -u, --username USERNAME      Single username
  -U, --userlist USERLIST      Usernames list
  -p, --password PASSWORD      Single password
  -P, --passlist PASSLIST      Passwords list
  -C, --combolist COMBOLIST    Combos username:password list
  -t, --threads THREADS        Number of threads [1-50] (default: 10)
  -s, --stoponsuccess          Stop on success
  -v, --verbose                Print every tested creds
  -e, --max-errors MAX_ERRORS  Number of accepted consecutive errors (default: 10)
  --timeout TIMEOUT            Time limit on the response (default: 20s)
  -l, --list-modules           Display list of modules
```

Example:
```
python3 web-brutator.py --target jenkins --url https://mytarget.com -U ./usernames.txt -P ./passwords.txt -s -t 40
```

# :rocket: Available Modules
- axis2
- coldfusion
- glassfish
- htaccess
- jboss
- jenkins
- joomla
- railo
- standardform
- tomcat
- weblogic
- websphere

*Notice: Some products implement account lockout after a given number of failed authentication attempts, by default (e.g. Weblogic, Tomcat...).
`web-brutator` notices the user at the beginning of bruteforce attack it is the case. Take this into account before launching bruteforce on such 
targets.*

# :bulb: Standard web authentication form Auto-Detection
`web-brutator` can automatically detect **standard** web authentication forms and perform bruteforce automatically.
This feature is available via the module `standardform`, it is **still experimental** and can lead to false positives/negatives 
since it is based on several heuristics. 

Not supported:
- Web authentication using Javascript;
- Authentication with CAPTCHA;
- 2-step authentication
...

Example:
```
python3 web-brutator.py --target standardform --url https://mytarget.com -U ./usernames.txt -P ./passwords.txt -s -t 40 -v
```
![Demo](./img/demo.gif)


# :wrench: Add new module / Contribute
Adding a new authentication bruteforce module is pretty straightforward:

1. Create a new file with appropriate name under `lib/core/modules/`
2. Create a class in this file, using the following template. Development is very easy, check any existing module 
under `lib/core/modules/` for some examples. Note that HTTP requests should be done via the static methods provided by
`Requester` class: `Requester.get()`, `Requester.post()`, `Requester.http_auth()`.
```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lib.core.Exceptions import AuthException, RequestException
from lib.core.Logger import logger
from lib.core.Requester import AuthMode, Requester


class Mymodule:

    def __init__(self, url, verbose=False):
        self.url = url
        # Other self variables can go here


    def check(self):
    	"""
    	This method is used to detect the presence of the targeted authentication
    	interface.
    	:return: Boolean indicating if the authentication interface has been detected
    	"""
    	# Implement code here


    def try_auth(self, username, password):
    	"""
    	This method is used to perform one authentication attempt.
    	:param str username: Username to check
    	:param str password: Password to check
    	:return: Boolean indicating authentication status
    	:raise AuthException:
    	"""
        # Implement code here        

```
3. Module is then automatically available (check using `-l` option) from the command-line.
4. Test the module to make sure it is working as expected !
5. Make a pull request to add the module to the project ;)