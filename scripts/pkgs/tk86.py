#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2017, Doug Massay

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re

from .constants import build_dir, CFLAGS, LDFLAGS, MAKEOPTS, LIBDIR, BIN, PREFIX, is64bit
from .utils import ModifiedEnv, run, replace_in_file


def main(args):
    conf = './configure --prefix={} --with-tcl={}'.format(build_dir(), LIBDIR)
    if is64bit:
        conf += ' --enable-64bit'
    # conf += ' {} {}'.format(CFLAGS, LDFLAGS)
    env = {'PATH': '{}:{}'.format(BIN, os.environ['PATH']), 'LD_LIBRARY_PATH': LIBDIR, 'CFLAGS': CFLAGS, 'LDFLAGS': LDFLAGS}

    os.chdir('unix')
    with ModifiedEnv(**env):
        # simple_build(conf)
        run(conf)
        run('make ' + MAKEOPTS)
        run('make install')
        run('make install-private-headers')
        run('ln -v -sf wish8.6 {}/bin/wish'.format(build_dir()))
        os.chmod('{}/lib/libtk8.6.so'.format(build_dir()), 0o755)
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/tk.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/tk.pc'), re.compile(br'^exec_prefix=.+$', re.M), b'exec_prefix=%s' % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/tk.pc'), re.compile(br'^libdir=.+$', re.M), b'libdir=%s/lib' % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tkConfig.sh'), re.compile(br'^TK_PREFIX=.+$', re.M), b"""TK_PREFIX='%s'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tkConfig.sh'), re.compile(br'^TK_EXEC_PREFIX=.+$', re.M), b"""TK_EXEC_PREFIX='%s'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tkConfig.sh'), re.compile(br'^TK_LIB_SPEC=.+$', re.M), b"""TK_LIB_SPEC='-L%s/lib -ltk8.6'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tkConfig.sh'), re.compile(br'^TK_INCLUDE_SPEC=.+$', re.M), b"""TK_INCLUDE_SPEC='-I%s/include'""" % PREFIX)
    # replace_in_file(os.path.join(build_dir(), 'lib/tkConfig.sh'), re.compile(br'^TK_PACKAGE_PATH=.+$', re.M), b"""TK_PACKAGE_PATH='%s/lib'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tkConfig.sh'), re.compile(br'^TK_STUB_LIB_SPEC=.+$', re.M), b"""TK_STUB_LIB_SPEC='-L%s/lib -ltkstub8.6'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tkConfig.sh'), re.compile(br'^TK_STUB_LIB_PATH=.+$', re.M), b"""TK_STUB_LIB_PATH='%s/lib/tkstub8.6.a'""" % PREFIX)
