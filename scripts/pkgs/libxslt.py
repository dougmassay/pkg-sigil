#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re

from .constants import PREFIX, build_dir, LIBDIR
from .utils import ModifiedEnv, simple_build, replace_in_file


def main(args):
    with ModifiedEnv(LD_LIBRARY_PATH=LIBDIR):
        simple_build(
            '--disable-dependency-tracking --disable-static --enable-shared --without-python --without-debug --without-crypto'
            ' --with-libxml-prefix={0} --with-libxml-include-prefix={0}/include/libxml2'.format(PREFIX))
        replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/libxslt.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
