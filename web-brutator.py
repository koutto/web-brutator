#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import colored
import sys
import traceback

from lib.core.ArgumentsParser import ArgumentsParser
from lib.core.Config import *
from lib.core.Controller import Controller
import lib.core.Globals as Globals
from lib.core.Logger import logger


class Program:

    def __init__(self):

        print(colored.stylize(BANNER, colored.attr('bold')))

        Globals.initialize()

        # Parse command-line arguments
        arguments = ArgumentsParser()

        # Controller
        try:
            controller = Controller(arguments.args)
            controller.run()
        except KeyboardInterrupt:
            logger.error('Canceled by the user')
            sys.exit(0)


if __name__ == '__main__':
    main = Program()