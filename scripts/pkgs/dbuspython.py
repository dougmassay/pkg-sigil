#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re

from .constants import PREFIX, build_dir, LIBDIR, PYTHON, py_ver
from .utils import ModifiedEnv, simple_build, run, replace_in_file


def main(args):
    env = {'PYTHON': PYTHON,
           'LD_LIBRARY_PATH': LIBDIR,
           # 'PYTHON_CONFIG': '{}/python{}m-config'.format(BIN, py_ver)}
           'PYTHON_INCLUDES': '-I{}/include/python{}m'.format(PREFIX, py_ver),
           'PYTHON_LIBS': '-L{}/lib -lpython{}m'.format(PREFIX, py_ver)}
    with ModifiedEnv(**env):
        simple_build()
        replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/dbus-python.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)


def post_install_check():
    run(PYTHON, '-c', 'from dbus.mainloop import glib', library_path=LIBDIR)
