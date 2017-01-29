#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import sys
import os
import tempfile

pkg_ext = 'pkg'
py_ver = '3.5'
icu_ver = '57'
tcl_ver = '8.6'


def uniq(vals):
    ''' Remove all duplicates from vals, while preserving order.  '''
    vals = vals or ()
    seen = set()
    seen_add = seen.add
    return list(x for x in vals if x not in seen and not seen_add(x))


ROOT = '/'
is64bit = sys.maxsize > (1 << 32)
SW = ROOT + 'sw'
SOURCES = ROOT + 'sources'
PATCHES = ROOT + 'patches'
SCRIPTS = ROOT + 'scripts'
SIGIL_SRC_DIR = ROOT + 'sigil-src'
PREFIX = os.path.join(SW, 'sw')
BIN = os.path.join(PREFIX, 'bin')
PYTHON = os.path.join(BIN, 'python3')
PATCHELF = os.path.join(BIN, 'patchelf')
MAKESELF = os.path.join(BIN, 'makeself.sh')
EXTRA_MANIFEST = os.path.join(SCRIPTS, 'sigil-extra-manifest.txt')
PKG_OUTPUT_DIR = os.path.join(SW, 'dist')
PY_COMPILE_FILE = 'compile_libs.py'
BASE_INSTALL_DIR = 'sigil'

worker_env = {}

CFLAGS = worker_env['CFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
CPPFLAGS = worker_env['CPPFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
LIBDIR = os.path.join(PREFIX, 'lib')
LDFLAGS = worker_env['LDFLAGS'] = '-L{0} -Wl,-rpath-link,{0}'.format(LIBDIR)

from multiprocessing import cpu_count

MAKEOPTS = '-j%d' % cpu_count()
PKG_CONFIG_PATH = worker_env['PKG_CONFIG_PATH'] = os.path.join(PREFIX, 'lib', 'pkgconfig')
CMAKE = os.path.join(BIN, 'cmake')

QT_PREFIX = os.path.join(PREFIX, 'qt')
QT_DLLS = ['libQt5%s.so.5' % x for x in (
    'Concurrent', 'Core', 'DBus', 'Gui', 'Multimedia', 'MultimediaWidgets', 'Network',
    'PrintSupport', 'Positioning', 'Qml', 'Quick', 'Sensors', 'Sql', 'Svg', 'WebChannel',
    'WebKit', 'WebKitWidgets', 'Widgets', 'OpenGL', 'XcbQpa', 'Xml', 'XmlPatterns'
)]
QT_PLUGINS = [
    'audio', 'bearer', 'iconengines', 'imageformats', 'mediaservice',
    'platforms', 'platforminputcontexts', 'position', 'printsupport',
    'sensors', 'sqldrivers', 'xcbglintegrations'
]
PYQT_MODULES = ['%s.so' % x for x in (
    'Qt', 'QtCore', 'QtGui', 'QtNetwork', 'QtMultimedia', 'QtMultimediaWidgets',
    'QtPrintSupport', 'QtSensors', 'QtSvg', 'QtWebKit', 'QtWebKitWidgets', 'QtWidgets'
)]

_build_dir = None


def build_dir():
    return _build_dir


def set_build_dir(x):
    global _build_dir
    _build_dir = x


_current_source = None


def current_source():
    return _current_source


def set_current_source(x):
    global _current_source
    _current_source = os.path.join(SOURCES, x)


_tdir = None


def set_tdir(x):
    global _tdir
    _tdir = x


def mkdtemp(prefix=''):
    return tempfile.mkdtemp(prefix=prefix, dir=_tdir)


def putenv(**kw):
    for key, val in kw.iteritems():
        if not val:
            worker_env.pop(key, None)
        else:
            worker_env[key] = val
