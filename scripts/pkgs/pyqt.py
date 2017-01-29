#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import PYTHON, py_ver, MAKEOPTS, build_dir, PREFIX
from .utils import run


def main(args):
    b = build_dir()
    lp = os.path.join(PREFIX, 'qt', 'lib')
    sip, qmake = 'sip', 'qmake'

    sp = 'lib/python{}'.format(py_ver)
    cmd = [PYTHON, 'configure.py', '--confirm-license', '--sip=%s/bin/%s' % (PREFIX, sip), '--qmake=%s/qt/bin/%s' % (PREFIX, qmake),
           '--bindir=%s/bin' % b, '--destdir=%s/%s/site-packages' % (b, sp), '--verbose', '--sipdir=%s/share/sip/PyQt5' % b,
           '--no-stubs', '-c', '-j5', '--no-designer-plugin', '--no-qml-plugin', '--no-docstrings']

    run(*cmd, library_path=lp)
    run('make ' + MAKEOPTS, library_path=lp)
    run('make install')


def post_install_check():
    run(PYTHON, '-c', 'import sip, sipconfig; from PyQt5 import QtCore, QtGui, QtWebKit', library_path=os.path.join(PREFIX, 'qt', 'lib'))
