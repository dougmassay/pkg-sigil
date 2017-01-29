#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import build_dir, CFLAGS, LIBDIR, PREFIX, PYTHON
from .utils import ModifiedEnv, run, simple_build


def main(args):
    # replace_in_file('setup.py', re.compile('def detect_tkinter.+:'), lambda m: m.group() + '\n' + ' ' * 8 + 'return 0')
    conf = (
        '--prefix={} --with-threads --enable-ipv6 --with-system-expat'
        ' --with-pymalloc --without-ensurepip --with-system-ffi --enable-shared').format(build_dir())
    env = {'CFLAGS': CFLAGS + ' -I{}/include/ncursesw'.format(PREFIX) + ' -DHAVE_LOAD_EXTENSION ',
           'LD_LIBRARY_PATH': LIBDIR}

    with ModifiedEnv(**env):
        simple_build(conf)


def filter_pkg(parts):
    if (
        'idlelib' in parts or 'ensurepip' in parts or 'config' in parts or
        'pydoc_data' in parts or 'Icons' in parts
    ):
        return True
    return False


def install_name_change_predicate(p):
    return p.endswith('/Python')


def post_install_check():
    mods = '_ssl zlib bz2 ctypes sqlite3 readline _curses _tkinter'.split()
    run(PYTHON, '-c', 'import ' + ','.join(mods), library_path=True)
