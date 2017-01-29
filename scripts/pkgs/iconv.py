#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .utils import apply_patch, simple_build


def main(args):
    apply_patch('iconv.patch')
    simple_build('--disable-dependency-tracking --disable-static --enable-shared')


def filter_pkg(parts):
    return 'locale' in parts
