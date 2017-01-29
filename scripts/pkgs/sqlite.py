#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import CFLAGS
from .utils import simple_build, ModifiedEnv


def main(args):
    cflags = CFLAGS
    with ModifiedEnv(CFLAGS=cflags):
        simple_build('--disable-dependency-tracking --disable-static')
