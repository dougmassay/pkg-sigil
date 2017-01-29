#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2017, Doug Massay

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re

from .constants import build_dir, MAKEOPTS, LIBDIR, PREFIX, is64bit
from .utils import ModifiedEnv, run, replace_in_file


def main(args):
    conf = './configure --prefix={} --with-tzdata=no'.format(build_dir())
    if is64bit:
        conf += ' --enable-64bit'
    # conf += ' {} {}'.format(CFLAGS, LDFLAGS)
    env = {'LD_LIBRARY_PATH': LIBDIR}

    os.chdir('unix')
    with ModifiedEnv(**env):
        # simple_build(conf)
        run(conf)
        run('make ' + MAKEOPTS)
        run('make install')
        run('make install-private-headers')
        run('ln -v -sf tclsh8.6 {}/bin/tclsh'.format(build_dir()))
        os.chmod('{}/lib/libtcl8.6.so'.format(build_dir()), 0o755)
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/tcl.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/tcl.pc'), re.compile(br'^exec_prefix=.+$', re.M), b'exec_prefix=%s' % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/tcl.pc'), re.compile(br'^libdir=.+$', re.M), b'libdir=%s/lib' % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tclConfig.sh'), re.compile(br'^TCL_PREFIX=.+$', re.M), b"""TCL_PREFIX='%s'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tclConfig.sh'), re.compile(br'^TCL_EXEC_PREFIX=.+$', re.M), b"""TCL_EXEC_PREFIX='%s'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tclConfig.sh'), re.compile(br'^TCL_LIB_SPEC=.+$', re.M), b"""TCL_LIB_SPEC='-L%s/lib -ltcl8.6'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tclConfig.sh'), re.compile(br'^TCL_INCLUDE_SPEC=.+$', re.M), b"""TCL_INCLUDE_SPEC='-I%s/include'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tclConfig.sh'), re.compile(br'^TCL_PACKAGE_PATH=.+$', re.M), b"""TCL_PACKAGE_PATH='%s/lib'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tclConfig.sh'), re.compile(br'^TCL_STUB_LIB_SPEC=.+$', re.M), b"""TCL_STUB_LIB_SPEC='-L%s/lib -ltclstub8.6'""" % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/tclConfig.sh'), re.compile(br'^TCL_STUB_LIB_PATH=.+$', re.M), b"""TCL_STUB_LIB_PATH='%s/lib/tclstub8.6.a'""" % PREFIX)
