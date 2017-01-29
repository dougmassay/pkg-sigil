#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import PYTHON, py_ver, MAKEOPTS, build_dir, PREFIX
from .utils import run, replace_in_file


def main(args):
    b = build_dir()
    cmd = [PYTHON, 'configure.py', '--bindir=%s/bin' % build_dir()]  # '--no-stubs'
    sp = 'lib/python{}'.format(py_ver)
    inc = 'include/python{}m'.format(py_ver)
    cmd += ['--destdir=%s/%s/site-packages' % (b, sp),
            '--sipdir=%s/share/sip' % b,
            '--incdir=%s/%s' % (b, inc)]
    run(*cmd, library_path=True)
    run('make ' + MAKEOPTS)
    run('make install')
    q, r = build_dir(), PREFIX
    p = 'lib/python{}'.format(py_ver)
    replace_in_file(os.path.join(b, p, 'site-packages/sipconfig.py'), q, r)
