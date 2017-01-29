#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import shutil
import os

from .constants import PREFIX, PYTHON, build_dir, SW, BIN
from .utils import ModifiedEnv, python_build, run


def main(args):
    with ModifiedEnv(PATH='{}:{}'.format(BIN, os.environ['PATH'])):
        run(PYTHON, *('setup.py build_ext -I {0}/include/libxml2 -L {0}/lib'.format(PREFIX).split()), library_path=True)
        python_build()
        ddir = 'lib'
        os.rename(os.path.join(build_dir(), os.path.basename(SW), os.path.basename(PREFIX), ddir), os.path.join(build_dir(), ddir))
        shutil.rmtree(os.path.join(build_dir(), os.path.basename(SW)))
