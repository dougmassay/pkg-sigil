#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil

from .constants import is64bit, CFLAGS, LDFLAGS, MAKEOPTS, build_dir
from .utils import run


def main(args):
    optflags = ['enable-ec_nistp_64_gcc_128'] if is64bit else []
    run('./config', '--prefix=/usr', '--openssldir=/etc/ssl', 'shared',
        'zlib', '-Wa,--noexecstack', CFLAGS, LDFLAGS, *optflags)
    run('make ' + MAKEOPTS)
    run('make test', library_path=os.getcwd())
    run('make', 'INSTALL_PREFIX={}'.format(build_dir()), 'install_sw')
    for x in 'bin lib include'.split():
        os.rename(os.path.join(build_dir(), 'usr', x), os.path.join(build_dir(), x))
    shutil.rmtree(os.path.join(build_dir(), 'lib', 'engines'))
