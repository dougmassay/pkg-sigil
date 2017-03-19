#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2017, Doug Massay

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re
import glob
import shutil
import errno
import subprocess

from .build_deps import init_env
from .constants import (mkdtemp, SW, MAKEOPTS, QT_PREFIX, LIBDIR, PREFIX,
                        PYTHON, PY_COMPILE_FILE, py_ver, MAKESELF, PKG_OUTPUT_DIR, CMAKE, BIN,
                        SIGIL_SRC_DIR, is64bit, set_build_dir)
from .utils import ModifiedEnv, run, run_shell, set_title


def get_sigil_version(x):
    _version_pattern = re.compile(br'SIGIL_FULL_VERSION="(.*?)"')
    with open(x, 'rb') as f:
        data = f.read()
        # data = data.decode('utf-8', 'ignore')
        m = _version_pattern.search(data)
        if m:
            _sigil_version = m.group(1).strip()
        return _sigil_version


def main(args):
    set_title('Building Sigil')
    init_env()
    base = PKG_OUTPUT_DIR
    try:
        shutil.rmtree(base)
    except EnvironmentError as err:
        if err.errno != errno.ENOENT:
            raise
    os.mkdir(base)
    build_dir = mkdtemp('build-')
    set_build_dir(build_dir)
    # installer_dir = os.path.join(build_dir, 'installer')
    cmake_prefix = os.path.join(QT_PREFIX, 'lib', 'cmake')
    pylib = 'libpython{}m.so'.format(py_ver)
    env = {'PATH': BIN + ':%s' % os.environ['PATH'], 'LD_LIBRARY_PATH': LIBDIR}

    cmd = [CMAKE, '-G', "Unix Makefiles",
           '-DCMAKE_PREFIX_PATH={}'.format(cmake_prefix),
           '-DCMAKE_BUILD_TYPE=Release',
           '-DPYTHON_LIBRARY={}/{}'.format(LIBDIR, pylib),
           '-DPYTHON_INCLUDE_DIR={}/include/python{}m'.format(PREFIX, py_ver),
           '-DPYTHON_EXECUTABLE={}'.format(PYTHON),
           '-DPKG_SYSTEM_PYTHON=1',
           SIGIL_SRC_DIR]

    with ModifiedEnv(**env):
        run_shell
        os.chdir(build_dir)
        run(*cmd)

        print(build_dir)
        make_flags_file = os.path.join(build_dir, 'src', 'CMakeFiles', 'sigil.dir', 'flags.make')
        sigil_ver = get_sigil_version(make_flags_file)
        installer_name = 'Sigil-v{}-Linux-{}'.format(sigil_ver, 'x86_64' if is64bit else 'x86')
        print('Package Name: ', installer_name)

        run('make ' + MAKEOPTS)

        from .create_sigil_pkg import main as freeze
        freeze()

        # run compile script that create_sigil_pkg dropped off.
        set_title('Pre-compiling Python modules')
        run(PYTHON, './{}'.format(PY_COMPILE_FILE))

        set_title('Creating Sigil installer package')
        run(MAKESELF, '--xz', '--keep-umask', os.path.join(build_dir, 'temp_folder'), os.path.join(PKG_OUTPUT_DIR,
                                                                                                   installer_name + '.xz.run'), 'Sigil Installer', './setup.sh')

        output = os.path.join(SW, 'dist')
        f = glob.glob('{}/Sigil-v*.xz.run'.format(output))
        if not len(f):
            raise ValueError('Output package not found in {}!'.format(output))
        else:
            name = os.path.join(PKG_OUTPUT_DIR, '{}.xz.run'.format(installer_name))
            with open(os.path.join(PKG_OUTPUT_DIR, 'sha256sum.txt'), 'wb') as f:
                subprocess.check_call(['sha256sum', name], stdout=f)
