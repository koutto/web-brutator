#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import glob
from os.path import basename

class Utils:

    @staticmethod
    def list_modules():
        modules = list(map(lambda x: basename(x)[:-3].lower(), 
            glob.glob('./lib/modules/*.py')))
        if '__init__' in modules:
            modules.remove('__init__')
        return sorted(modules)


class LineWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):

    def _split_lines(self, text, width):
        """
        For custom max width
        """
        #text = self._whitespace_matcher.sub(' ', text).strip()
        #return textwrap.wrap(text, ARGPARSE_MAX_WIDTH)
        return text.splitlines()


    def _format_args(self, action, default_metavar):
        """
        For multi args (nargs >= 2), do not use default syntax (ARG [ARG ...])
        """
        get_metavar = self._metavar_formatter(action, default_metavar)
        if action.nargs == argparse.ONE_OR_MORE:
            return get_metavar(1)[0]
        else:
            return super()._format_args(action, default_metavar)


    def _format_action_invocation(self, action):
        """
        Custom for concatenation short and long option with only one occurrence of metavar
        """
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar
        else:
            parts = []

            # If the Optional doesn't take a value, format is: -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # If the Optional takes a value, format is: -s ARGS, --long ARGS
            else:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append(option_string)

                return '%s %s' % (', '.join(parts), args_string)

            return ', '.join(parts)


    def _get_default_metavar_for_optional(self, action):
        return action.dest.upper()


    def _get_default_metavar_for_positional(self, action):
        return action.dest.upper()
