#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import CFLAGS, LDFLAGS, MAKEOPTS, build_dir
from .utils import run, run_shell, replace_in_file


def main(args):
    # Change pointing_hand to hand2, see
    # https://bugreports.qt.io/browse/QTBUG-41151
    replace_in_file('qtbase/src/plugins/platforms/xcb/qxcbcursor.cpp', 'pointing_hand"', 'hand2"')
    cflags, ldflags = CFLAGS, LDFLAGS
    os.mkdir('build'), os.chdir('build')
    configure = '../configure'
    # Slim down Qt
    # For the list of modules and their dependencies, see .gitmodules
    skip_modules = (
        # To add web engine remove qtwebengine and qtwebview from this list
        'qtconnectivity qtactiveqt qtscript qtdoc qt3d qtwebengine'
        ' qtgraphicaleffects qtquickcontrols qtquickcontrols2'
    ).split()
    conf = configure + (
        ' -v -opensource -confirm-license -prefix {}/qt -release -nomake examples -nomake tests'
        ' -opengl -no-openssl -no-sql-odbc -no-sql-psql -no-qml-debug -icu -qt-harfbuzz'
        ' -qt-xcb -qt-xkbcommon-x11 -glib -no-gtkstyle -qt-pcre -gstreamer'
    ).format(build_dir())
    skip_modules = ' '.join('-skip ' + x for x in skip_modules)
    conf += ' ' + skip_modules + ' ' + cflags + ' ' + ldflags
    run(conf, library_path=True)
    # run_shell()
    run_shell
    run('make ' + MAKEOPTS, library_path=True)
    run('make install')
    with open(os.path.join(build_dir(), 'qt', 'bin', 'qt.conf'), 'wb') as f:
        f.write(b"[Paths]\nPrefix = ..\n")
