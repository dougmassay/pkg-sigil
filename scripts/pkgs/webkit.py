#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil

from .constants import MAKEOPTS, build_dir, PREFIX
from .utils import run, run_shell, ModifiedEnv


def main(args):
    lp = os.path.join(PREFIX, 'qt', 'lib')
    bdir = os.path.join(build_dir(), 'qt')
    qmake = os.path.join(PREFIX, 'qt', 'bin', 'qmake')
    env = {}
    os.mkdir('build'), os.chdir('build')
    with ModifiedEnv(**env):
        run(qmake, 'PREFIX=' + bdir.replace(os.sep, '/'), '..', library_path=lp)
        # run_shell()
        run_shell
        run('make ' + MAKEOPTS, library_path=lp)
        run('make INSTALL_ROOT=%s install' % bdir)
        idir = os.path.join(bdir, 'sw', 'sw', 'qt')
        for x in os.listdir(idir):
            os.rename(os.path.join(idir, x), os.path.join(bdir, x))
        shutil.rmtree(os.path.join(bdir, 'sw'))
