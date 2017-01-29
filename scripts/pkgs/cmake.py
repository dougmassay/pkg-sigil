#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .utils import simple_build


def main(args):
    simple_build('--no-qt-gui', configure_name='./bootstrap')


def filter_pkg(parts):
    return 'Help' in parts


pkg_exclude_extensions = frozenset()
