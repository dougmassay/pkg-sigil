#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import re
import os

from .constants import LIBDIR, PREFIX, build_dir
from .utils import simple_build, ModifiedEnv, replace_in_file


def main(args):
    env = {'LIBFFI_CFLAGS': '-I{}/include'.format(PREFIX), 'LIBFFI_LIBS': '-L{}/lib -lffi'.format(PREFIX),
           'ZLIB_CFLAGS': '-I{}/include'.format(PREFIX), 'ZLIB_LIBS': '-L{}/lib -lz'.format(PREFIX), 'LD_LIBRARY_PATH': LIBDIR}
    with ModifiedEnv(**env):
        simple_build('--disable-dependency-tracking --disable-static --with-python={}/bin/python3 --disable-selinux'
                     '--disable-fam --with-libiconv=gnu --with-pcre=internal'.format(PREFIX))
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/glib-2.0.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
