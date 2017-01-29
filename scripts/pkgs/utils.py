#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# Sigil adaptations made by Doug Massay 2017

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
from contextlib import contextmanager
import time
import os
import shlex
import pipes
import subprocess
import sys
import errno
import glob
import shutil
import zipfile

from .constants import build_dir, current_source, mkdtemp, PATCHES, PYTHON, MAKEOPTS, LIBDIR, worker_env


split = shlex.split
issymlink = os.path.islink


class ModifiedEnv(object):

    def __init__(self, **kwargs):
        self.mods = kwargs

    def apply(self, mods):
        for k, val in mods.iteritems():
            if val:
                worker_env[k] = val
            else:
                worker_env.pop(k, None)

    def __enter__(self):
        self.orig = {k: worker_env.get(k) for k in self.mods}
        self.apply(self.mods)

    def __exit__(self, *args):
        self.apply(self.orig)


def current_env(library_path=False):
    env = os.environ.copy()
    env.update(worker_env)
    if library_path:
        if library_path is True:
            library_path = LIBDIR
        else:
            library_path = library_path + os.pathsep + LIBDIR
        env['LD_LIBRARY_PATH'] = library_path
    enc = 'utf-8'
    env = {k.encode(enc): v.encode(enc) for k, v in env.iteritems()}
    return env


def run_shell(library_path=False):
    sh = '/bin/bash'
    env = current_env(library_path=library_path)
    return subprocess.Popen([sh, '-i'], env=env).wait()


def run(*args, **kw):
    if len(args) == 1 and isinstance(args[0], type('')):
        cmd = split(args[0])
    else:
        cmd = args
    print(' '.join(pipes.quote(x) for x in cmd))
    sys.stdout.flush()
    env = current_env(library_path=kw.get('library_path'))
    try:
        p = subprocess.Popen(cmd, env=env, cwd=kw.get('cwd'))
    except EnvironmentError as err:
        if err.errno == errno.ENOENT:
            raise SystemExit('Could not find the program: %s' % cmd[0])
        raise
    rc = p.wait()
    if kw.get('no_check'):
        return rc
    if rc != 0:
        print('The following command failed, with return code:', rc)
        print(' '.join(pipes.quote(x) for x in cmd))
        print('Dropping you into a shell')
        sys.stdout.flush()
        run_shell(library_path=kw.get('library_path'))
        raise SystemExit(1)


def extract(source):
    if source.lower().endswith('.zip'):
        with zipfile.ZipFile(source) as zf:
            zf.extractall()
    else:
        env = {}
        tar = 'tar'
        with ModifiedEnv(**env):
            run(tar, 'xf', source)


def chdir_for_extract(name):
    tdir = mkdtemp(prefix=os.path.basename(name).split('-')[0] + '-')
    os.chdir(tdir)
    return tdir


def extract_source():
    source = current_source()
    tdir = chdir_for_extract(source)
    print('Extracting source:', source)
    sys.stdout.flush()
    extract(source)
    x = os.listdir('.')
    if len(x) == 1:
        os.chdir(x[0])
    return tdir


def apply_patch(name, level=0, reverse=False, convert_line_endings=False):
    if not os.path.isabs(name):
        name = os.path.join(PATCHES, name)
    patch = 'patch'
    args = [patch, '-p%d' % level, '-i', name]
    if reverse:
        args.insert(1, '-R')
    run(*args)


def simple_build(configure_args=(), make_args=(), install_args=(), library_path=None, override_prefix=None, no_parallel=False, configure_name='./configure'):
    if isinstance(configure_args, type('')):
        configure_args = split(configure_args)
    if isinstance(make_args, type('')):
        make_args = split(make_args)
    if isinstance(install_args, type('')):
        install_args = split(install_args)
    run(configure_name, '--prefix=' + (override_prefix or build_dir()), *configure_args)
    make_opts = [] if no_parallel else split(MAKEOPTS)
    run('make', *(make_opts + list(make_args)))
    mi = ['make'] + list(install_args) + ['install']
    run(*mi, library_path=library_path)


def python_build(extra_args=()):
    if isinstance(extra_args, type('')):
        extra_args = split(extra_args)
    run(PYTHON, 'setup.py', 'install', '--root', build_dir(), *extra_args, library_path=True)


def replace_in_file(path, old, new, missing_ok=False):
    if isinstance(old, type('')):
        old = old.encode('utf-8')
    if isinstance(new, type('')):
        new = new.encode('utf-8')
    with open(path, 'r+b') as f:
        raw = f.read()
        if isinstance(old, bytes):
            nraw = raw.replace(old, new)
        else:
            nraw = old.sub(new, raw)
        if raw == nraw and not missing_ok:
            raise ValueError('Failed (pattern not found) to patch: ' + path)
        f.seek(0), f.truncate()
        f.write(nraw)


hardlink = os.link
rmtree = shutil.rmtree


def lcopy(src, dst, no_hardlinks=False):
    try:
        if issymlink(src):
            linkto = os.readlink(src)
            os.symlink(linkto, dst)
            return True
        else:
            if no_hardlinks:
                shutil.copy(src, dst)
            else:
                hardlink(src, dst)
            return False
    except EnvironmentError as err:
        if err.errno == errno.EEXIST:
            os.unlink(dst)
            return lcopy(src, dst)
        raise


def install_binaries(pattern, destdir='lib', do_symlinks=False, fname_map=os.path.basename):
    dest = os.path.join(build_dir(), destdir)
    ensure_dir(dest)
    files = glob.glob(pattern)
    files.sort(key=len, reverse=True)
    if not files:
        raise ValueError('The pattern %s did not match any actual files' % pattern)
    for f in files:
        dst = os.path.join(dest, fname_map(f))
        islink = lcopy(f, dst)
        if not islink:
            os.chmod(dst, 0o755)
    if do_symlinks:
        library_symlinks(files[0], destdir=destdir)


def install_tree(src, dest_parent='include', ignore=None):
    dest_parent = os.path.join(build_dir(), dest_parent)
    dst = os.path.join(dest_parent, os.path.basename(src))
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True, ignore=ignore)
    return dst


def copy_headers(pattern, destdir='include'):
    dest = os.path.join(build_dir(), destdir)
    ensure_dir(dest)
    files = glob.glob(pattern)
    for f in files:
        dst = os.path.join(dest, os.path.basename(f))
        if os.path.isdir(f):
            shutil.copytree(f, dst)
        else:
            shutil.copy2(f, dst)


def library_symlinks(full_name, destdir='lib'):
    parts = full_name.split('.')
    idx = parts.index('so')
    basename = '.'.join(parts[:idx + 1])
    parts = parts[idx + 1:]
    for i in range(len(parts)):
        suffix = '.'.join(parts[:i])
        if suffix:
            suffix = '.' + suffix
        ln = os.path.join(build_dir(), destdir, basename + suffix)
        try:
            os.symlink(full_name, ln)
        except EnvironmentError as err:
            if err.errno != errno.EEXIST:
                raise
            os.unlink(ln)
            os.symlink(full_name, ln)


def ensure_dir(path):
    try:
        os.makedirs(path)
    except EnvironmentError as err:
        if err.errno != errno.EEXIST:
            raise


def create_package(module, src_dir, outpath):

    exclude = getattr(module, 'pkg_exclude_names', frozenset('doc man info test tests gtk-doc README'.split()))
    exclude_extensions = getattr(module, 'pkg_exclude_extensions', frozenset(('pyc', 'pyo', 'la', 'chm', 'cpp', 'rst', 'md')))

    try:
        shutil.rmtree(outpath)
    except EnvironmentError as err:
        if err.errno != errno.ENOENT:
            raise

    os.mkdir(outpath)

    for dirpath, dirnames, filenames in os.walk(src_dir):

        def get_name(x):
            return os.path.relpath(os.path.join(dirpath, x), src_dir).replace(os.sep, '/')

        def is_ok(name):
            parts = name.split('/')
            for p in parts:
                if p in exclude or p.rpartition('.')[-1] in exclude_extensions:
                    return False
            if hasattr(module, 'filter_pkg') and module.filter_pkg(parts):
                return False
            return True

        for d in tuple(dirnames):
            if issymlink(os.path.join(dirpath, d)):
                dirnames.remove(d)
                filenames.append(d)
                continue
            name = get_name(d)
            if is_ok(name):
                try:
                    os.makedirs(os.path.join(outpath, name))
                except EnvironmentError as err:
                    if err.errno != errno.EEXIST:
                        raise
            else:
                dirnames.remove(d)

        for f in filenames:
            name = get_name(f)
            if is_ok(name):
                # on linux hardlinking fails because the package is
                # built in tmpfs and outpath is on a different volume
                lcopy(os.path.join(dirpath, f), os.path.join(outpath, name), no_hardlinks=True)


def install_package(pkg_path, dest_dir):
    for dirpath, dirnames, filenames in os.walk(pkg_path):
        for x in tuple(dirnames):
            d = os.path.join(dirpath, x)
            if issymlink(d):
                filenames.append(x)
                dirnames.remove(x)
                continue
            name = os.path.relpath(d, pkg_path)
            try:
                os.makedirs(os.path.join(dest_dir, name))
            except EnvironmentError as err:
                if err.errno != errno.EEXIST:
                    raise
        for x in filenames:
            f = os.path.join(dirpath, x)
            name = os.path.relpath(f, pkg_path)
            lcopy(f, os.path.join(dest_dir, name))


def set_title(x):
    if sys.stdout.isatty():
        print('''\033]2;%s\007''' % x)


def walk(path='.'):
    ''' A nice interface to os.walk '''
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            yield os.path.join(dirpath, f)


@contextmanager
def timeit():
    ' Usage: `with timeit() as times: whatever()` minutes, seconds = times '
    times = [0, 0]
    st = time.time()
    yield times
    dt = time.time() - st
    times[0], times[1] = dt // 60, dt % 60


@contextmanager
def current_dir(path):
    cwd = os.getcwd()
    os.chdir(path)
    yield path
    os.chdir(cwd)


@contextmanager
def tempdir(prefix='tmp-'):
    tdir = mkdtemp(prefix)
    yield tdir
    try:
        shutil.rmtree(tdir)
    except EnvironmentError:
        time.sleep(10)  # idiotic windows mandatory file locking
        shutil.rmtree(tdir)
