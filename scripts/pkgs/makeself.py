#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import build_dir
from .utils import run


def main(args):
    r = os.path.join(build_dir(), 'bin')
    os.makedirs(r)
    run('cp -v ./makeself.sh {}/'.format(r))
    run('cp -v ./makeself-header.sh {}/'.format(r))


def post_install_check():
    run('{}/makeself.sh -v'.format(os.path.join(build_dir(), 'bin')))
