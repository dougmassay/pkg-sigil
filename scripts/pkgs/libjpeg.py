#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .utils import simple_build


def main(args):
    conf = ' --disable-dependency-tracking --enable-shared --with-jpeg8 --without-turbojpeg --disable-static'
    simple_build(conf)
