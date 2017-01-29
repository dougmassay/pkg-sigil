#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
import re

from .constants import PREFIX, build_dir
from .utils import replace_in_file, simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(PATH='{}/bin:{}'.format(PREFIX, os.environ['PATH'])):
        simple_build('--disable-dependency-tracking --disable-static')
        replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/dbus-glib-1.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
