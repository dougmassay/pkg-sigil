#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2017, Doug Massay

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import build_dir
from .utils import simple_build, run


def main(args):
    simple_build()


def post_install_check():
    run('{}/patchelf --version'.format(os.path.join(build_dir(), 'bin')))
