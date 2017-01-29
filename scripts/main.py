#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import argparse
import shutil
import tempfile
import sys

args = sys.argv

from pkgs.constants import SW, pkg_ext
from pkgs.utils import run_shell


if hasattr(os, 'geteuid') and os.geteuid() == 0:
    import pwd
    uid, gid = pwd.getpwnam('sigil').pw_uid, pwd.getpwnam('sigil').pw_gid
    os.chown(SW, uid, gid)
    os.setgid(gid), os.setuid(uid)

os.environ['HOME'] = tempfile.gettempdir()
os.chdir(tempfile.gettempdir())

parser = argparse.ArgumentParser(description='Build Sigil dependencies')
a = parser.add_argument
a('deps', nargs='*', default=[], help='Which dependencies to build')
a('--shell', default=False, action='store_true',
  help='Start a shell in the container')
a('--clean', default=False, action='store_true',
  help='Remove previously built packages')

args = parser.parse_args(args[1:])

if args.shell or args.deps == ['shell']:
    from pkgs.build_deps import init_env
    dest_dir = init_env()
    try:
        raise SystemExit(run_shell(True))
    finally:
        shutil.rmtree(dest_dir)

if args.deps == ['sigil']:
    from pkgs.build_sigil import main
    main(args)
else:
    from pkgs.build_deps import main
    if args.clean:
        for x in os.listdir(SW):
            if x.endswith('.' + pkg_ext):
                shutil.rmtree(os.path.join(SW, x))
    main(args)
