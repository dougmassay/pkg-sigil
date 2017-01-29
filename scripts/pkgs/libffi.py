#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import re
import os

from .constants import PREFIX, build_dir
from .utils import apply_patch, simple_build, replace_in_file


def main(args):
    # Normalizes libffi's crazy installed include file's location
    apply_patch('libffi-3.2.1.patch', level=1)
    simple_build('--disable-static --enable-pax_emutramp')
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/libffi.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
