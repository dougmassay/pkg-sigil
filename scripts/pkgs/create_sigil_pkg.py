#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
# License: GPLv3 Copyright: 2017, Doug Massay

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
import shutil
import subprocess
import glob
import textwrap

from .constants import (py_ver, icu_ver, tcl_ver, build_dir, is64bit,
                        SIGIL_SRC_DIR, PYTHON, EXTRA_MANIFEST, PY_COMPILE_FILE, PATCHELF, LIBDIR,
                        BASE_INSTALL_DIR, QT_PREFIX, QT_DLLS, QT_PLUGINS, PYQT_MODULES, EXCLUDED_UIC_WIDGET_PLUGINS)


compile_code = textwrap.dedent('''\
        #!/usr/bin/env python3

        import os
        import py_compile

        for x in os.walk('{0}'):
            for f in x[-1]:
                if f.endswith('.py'):
                    y = os.path.join(x[0], f)
                    rel = os.path.relpath(y, '{0}')
                    try:
                        py_compile.compile(y, cfile=y+'c',dfile=rel, doraise=True, optimize=2)
                        os.remove(y)
                        z = y+'o'
                        if os.path.exists(z):
                            os.remove(z)
                    except:
                        print ('Failed to byte-compile', y)
        ''')


launcher_bash = textwrap.dedent('''\
        #!/bin/sh

        # Entry point for Sigil on Unix systems.

        INST_DIR={}

        SIGIL_PREFS_DIR="$HOME/.local/share/bundled-sigil-ebook/sigil"
        export SIGIL_PREFS_DIR

        # Consolidate all of Sigil's files in one directory
        if [ -z "$SIGIL_EXTRA_ROOT" ]; then
          SIGIL_EXTRA_ROOT=$INST_DIR
          export SIGIL_EXTRA_ROOT
        fi

        exec "$INST_DIR/sigil" "$@"
        ''')

site_code = textwrap.dedent('''\
        import sys
        import builtins
        import os
        import _sitebuiltins

        def set_helper():
            builtins.help = _sitebuiltins._Helper()

        def fix_sys_path():
            if os.sep == '/':
                for path in sys.path:
                    py_ver = "".join(map(str, sys.version[:3])).replace(".", "")
                    if os.path.basename(path) == "python" + py_ver + ".zip":
                        sys.path.remove(path)
                sys.path.append(os.path.join(sys.prefix, "lib",
                                "python" + sys.version[:3],
                                "site-packages"))
            else:
                for path in sys.path:
                    py_ver = "".join(map(str, sys.version[:3])).replace(".", "")
                    if os.path.basename(path) == "python" + py_ver + ".zip":
                        sys.path.remove(path)
                sys.path.append(os.path.join(sys.prefix, "lib", "site-packages"))

        def main():
            try:
                fix_sys_path()
                set_helper()
            except SystemExit as err:
                if err.code is None:
                    return 0
                if isinstance(err.code, int):
                    return err.code
                print (err.code)
                return 1
            except:
                import traceback
                traceback.print_exc()
            return 1

        if not sys.flags.no_site:
            main()
            ''')

setup_bash = '''\
#!/bin/bash

version_lt() {{
    test "$(printf '%s\n' "$@" | sort -t. -k 1,1nr -k 2,2nr -k 3,3nr -k 4,4nr | head -n 1)" != "$1";
}}

MINIMUMLIBC="2.19"
SYSTEMLIBC="$(ldd --version | awk '/ldd/{{print $NF}}')"

SKIPLIBCTEST=0
if [ "$1" = "skiplibctest" ]; then
    SKIPLIBCTEST=1
fi

if [ $SKIPLIBCTEST -ne 1 ]; then
    if version_lt $SYSTEMLIBC $MINIMUMLIBC; then
        printf "You need libc version $MINIMUMLIBC or greater to run Sigil ($SYSTEMLIBC was found) -- aborting!\\n"
        exit 1
    fi
else
    printf "Overriding glibc version check!\\n"
fi

if [ $(id -u) -ne 0 ]; then
    HOME="$(getent passwd "$USER" | cut -d: -f6)"
    DEST="$HOME/opt"
    LAUNCHER=./user_sigil.sh
    PYVENV=./user_pyvenv.cfg
    DESKTOP="$HOME/.local/share/applications"
    UNINSTALL=./remove_sigil_user
    #sed -ie "s|^Exec=sigil|Exec=$HOME/bin/sigil|g" ./sigil.desktop
    #sed -ie "s|^TryExec=sigil|TryExec=$HOME/bin/sigil|g" ./sigil.desktop
    perl -pi -e "s!Exec=sigil!Exec=$HOME/bin/sigil!g" ./sigil.desktop
    perl -pi -e "s!TryExec=sigil!TryExec=$HOME/bin/sigil!g" ./sigil.desktop
    chmod a+x ./sigil.desktop
    ICON="$HOME/.icons"
    BINDIR="$HOME/bin"
    MSG="Continue with the installation of Sigil to $DEST/{0}? (rerun the installer with root privileges to install Sigil system-wide)"
else
    DEST=/opt
    LAUNCHER=./system_sigil.sh
    PYVENV=./system_pyvenv.cfg
    DESKTOP=/usr/share/applications
    UNINSTALL=./remove_sigil_root
    #perl -pi -e "s!launch_root!launch!g" ./remove_sigil
    #perl -pi -e "s!paths_root!paths!g" ./remove_sigil
    ICON=/usr/share/pixmaps
    BINDIR=/usr/bin
    MSG="Continue with the installation of Sigil to /opt/{0}? (rerun the installer WITHOUT root privileges to install Sigil to your home directory)"
fi

read -r -p "$MSG [y/N] " response
case $response in
    [yY][eE][sS]|[yY])
        if [ -d "$DEST/{0}" ]; then
            rm -rf "$DEST/{0}"
        fi
        if [ ! -d "$DEST" ] && [ $(id -u) -ne 0 ]; then
            mkdir -p "$DEST"
        fi
        printf "\\nCopying files to $DEST/{0} ...\\n"
        \cp -rf ./{0} "$DEST/{0}"
        \cp -f "$LAUNCHER" "$DEST/{0}/sigil.sh"
        \cp -f "$PYVENV" "$DEST/{0}/python3/pyvenv.cfg"
        \cp -f "$UNINSTALL" "$DEST/{0}/remove_sigil"

        printf "\\nCreating link(s) ...\\n"
        if [ ! -d "$BINDIR" ] && [ $(id -u) -ne 0 ]; then
            mkdir -p "$BINDIR"
        fi
        ln -sfv "$DEST/{0}/sigil.sh" "$BINDIR/sigil"

        printf "\\nCreating desktop and icon entries ...\\n"
        if [ ! -d "$ICON" ] && [ $(id -u) -ne 0 ]; then
            mkdir -p "$ICON"
        fi
        \cp -fv ./app_icon_48.png "$ICON/sigil.png"

        sleep 2
        if [ ! -d "$DESKTOP" ] && [ $(id -u) -ne 0 ]; then
            mkdir -p "$DESKTOP"
        fi
        \cp -fv ./sigil.desktop "$DESKTOP/sigil.desktop"

        #touch -d -c "$DESKTOP/sigil.desktop"

        printf "\\nSigil installation complete.\\n"
        ;;
    *)
        printf "\\nSigil installation cancelled.\\n"
        exit 1
        ;;
esac
'''

user_paths = { 'launch'  : "os.path.expanduser('~/bin/sigil')",
               'path'    : "os.path.expanduser('~/opt/sigil')",
               'desktop' : "os.path.expanduser('~/.local/share/applications/sigil.desktop')",
               'icon'    : "os.path.expanduser('~/.icons/sigil.png')" }

root_paths = { 'launch'  : "'/usr/bin/sigil'",
               'path'    : "'/opt/sigil'",
               'desktop' : "'/usr/share/applications/sigil.desktop'",
               'icon'    : "'/usr/share/pixmaps/sigil.png'" }

uninstall_script = textwrap.dedent('''\
        #!/usr/bin/env python

        from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

        import os
        import shutil

        def main():
            launch = {launch}
            paths = {{
                'path'    : {path},
                'desktop' : {desktop},
                'icon'    : {icon}
            }}

            if os.path.islink(launch):
                print("Removing the '{{}}' link from '{{}}'.".format(os.path.basename(launch), os.path.dirname(launch)))
                os.unlink(launch)

            for k, v in paths.items():
                if k == 'path' and os.path.exists(v) and os.path.isdir(v):
                    print("Removing the '{{}}' directory from '{{}}'.".format(os.path.basename(v), os.path.dirname(v)))
                    shutil.rmtree(v)
                elif os.path.exists(v) and os.path.isfile(v):
                    print("Removing the '{{}}' file from '{{}}'.".format(os.path.basename(v), os.path.dirname(v)))
                    os.remove(v)
                else:
                    print("'{{}}' not found in '{{}}'. Nothing done.".format(os.path.basename(v), os.path.dirname(v)))


        if __name__ == '__main__':
            main()
        ''')

# Python standard modules location
PYTHON_SRC = os.path.join(LIBDIR, 'python{}'.format(py_ver))
temp_folder = os.path.join(build_dir(), 'temp_folder')
app_folder = os.path.join(temp_folder, BASE_INSTALL_DIR)
py_dest = os.path.join(app_folder, 'python3')
# Where we're going to copy stuff
py_dir = os.path.join(py_dest, 'lib', os.path.basename(PYTHON_SRC))
site_dest = os.path.join(py_dir, 'site-packages')

if os.path.exists(temp_folder) and os.path.isdir(temp_folder):
    shutil.rmtree(temp_folder)

os.makedirs(py_dir)
os.makedirs(os.path.join(py_dest, 'bin'))


def set_rpath(f, depth=0):
    if depth == 0:
        subprocess.check_call([PATCHELF, '--set-rpath', '$ORIGIN', f])
        print('Setting rpath of {} to $ORIGIN'.format(os.path.basename(f)))
        return
    else:
        recurse = ''.join(['../' for x in range(depth)])
        rpath = '$ORIGIN/{}{}'.format(recurse, BASE_INSTALL_DIR)
        subprocess.check_call([PATCHELF, '--set-rpath', rpath, f])
        print('Setting rpath of {} to {}'.format(os.path.basename(f), rpath))
        return


regex_lib = '_regex.cpython-35m-i386-linux-gnu.so'
if is64bit:
    regex_lib = '_regex.cpython-35m-x86_64-linux-gnu.so'
    
# Cherry-picked additional and/or modified modules
site_packages = [ ('lxml', 'd'),
                  ('six.py', 'f'),
                  ('html5lib', 'd'),
                  ('PIL', 'd'),
                  ('regex.py', 'f'),
                  (regex_lib, 'f'),
                  ('_regex_core.py', 'f'),
                  ('test_regex.py', 'f'),
                  ('cssselect', 'd'),
                  ('encutils', 'd'),
                  ('cssutils', 'd'),
                  ('webencodings', 'd'),
                  ('chardet', 'd'),
                  # ('dbus', 'd'),
                  # ('_dbus_bindings.so', 'f'),
                  # ('_dbus_glib_bindings.so', 'f'),
                  ('sip.so', 'f'),
                  ('PyQt5', 'd') ]


def copy_site_packages(packages, dest):
    for pkg, typ in packages:
        found = False
        sitepath = os.path.join(PYTHON_SRC, 'site-packages')
        if not found:
            for entry in os.listdir(sitepath):
                if entry == pkg:
                    if typ == 'd' and os.path.isdir(os.path.join(sitepath, entry)):
                        if pkg == 'PyQt5':
                            shutil.copytree(os.path.join(sitepath, entry), os.path.join(site_dest, entry), ignore=ignore_in_pyqt5_dirs)
                            for module_name in os.listdir(os.path.join(site_dest, entry)):
                                # Set RPATH in bundled PyQt5 shared libraries to root lib dir
                                if os.path.isfile(os.path.join(site_dest, entry, module_name)) and module_name.rpartition('.')[-1] == 'so' and module_name != 'Qt.so':
                                    set_rpath(os.path.join(site_dest, entry, module_name), depth=6)
                        else:
                            shutil.copytree(os.path.join(sitepath, entry), os.path.join(site_dest, entry), ignore=ignore_in_dirs)
                        found = True
                        break
                    else:
                        if os.path.isfile(os.path.join(sitepath, entry)):
                            shutil.copy2(os.path.join(sitepath, entry), os.path.join(site_dest, entry))
                            found = True
                            break
        else:
            break


def ignore_in_pyqt5_dirs(base, items, ignored_dirs=None):
    ans = []
    if ignored_dirs is None:
        ignored_dirs = {'.svn', '.bzr', '.git', 'doc', 'examples', 'includes', 'mkspecs',
                       'plugins', 'qml', 'qsci', 'qt', 'sip', 'translations', 'port_v2', '__pycache__'}
    for name in items:
        path = os.path.join(base, name)
        if os.path.isdir(path):
            if name in ignored_dirs or not os.path.exists(os.path.join(path, '__init__.py')):
                ans.append(name)
        else:
            if name.rpartition('.')[-1] not in ('so', 'py'):
                ans.append(name)
            if name.rpartition('.')[-1] == 'so' and name not in PYQT_MODULES:
                ans.append(name)
            if name.rpartition('.')[-1] == 'py' and name in EXCLUDED_UIC_WIDGET_PLUGINS:
                ans.append(name)
    return ans


def ignore_in_dirs(base, items, ignored_dirs=None):
    ans = []
    if ignored_dirs is None:
        ignored_dirs = {'.svn', '.bzr', '.git', 'doc', 'test', 'tests', 'testing', '__pycache__'}
    for name in items:
        path = os.path.join(base, name)
        if os.path.isdir(path):
            if name in ignored_dirs or not os.path.exists(os.path.join(path, '__init__.py')):
                ans.append(name)
        else:
            if name.rpartition('.')[-1] not in ('so', 'py'):
                ans.append(name)
    return ans


def copy_pylib():
    py_lib = os.path.join(LIBDIR, 'libpython{}m.so.1.0'.format(py_ver))
    shutil.copy2(py_lib, app_folder)
    os.chmod(os.path.join(app_folder, os.path.basename(py_lib)), 0o755)
    set_rpath(os.path.join(app_folder, os.path.basename(py_lib)))
    shutil.copy2(PYTHON, os.path.join(py_dest, 'bin', 'python3'))
    set_rpath(os.path.join(py_dest, 'bin', 'python3'), depth=3)


def copy_python():
    if not os.path.exists(py_dir):
        os.mkdir(py_dir)

    for x in os.listdir(PYTHON_SRC):
        y = os.path.join(PYTHON_SRC, x)
        ext = os.path.splitext(x)[1]
        if os.path.isdir(y) and x not in ('test', 'hotshot', 'distutils',
                'site-packages', 'idlelib', 'lib2to3', 'dist-packages', '__pycache__'):
            shutil.copytree(y, os.path.join(py_dir, x),
                    ignore=ignore_in_dirs)
        if os.path.isfile(y) and ext in ('.py', '.so'):
            shutil.copy2(y, py_dir)

    # Set RPATH for shared libraries in lib-dynload to root lib dir
    root = os.path.join(py_dir, 'lib-dynload')
    for item in os.listdir(root):
        f = os.path.join(root, item)
        if os.path.isfile(f) and os.path.splitext(f)[1] == '.so':
            set_rpath(f, depth=5)


def copy_tcltk():
    tk_lib = os.path.join(LIBDIR, 'libtk{}.so'.format(tcl_ver))
    shutil.copy2(tk_lib, app_folder)
    set_rpath(os.path.join(app_folder, os.path.basename(tk_lib)))
    tcl_lib = os.path.join(LIBDIR, 'libtcl{}.so'.format(tcl_ver))
    shutil.copy2(tcl_lib, app_folder)
    set_rpath(os.path.join(app_folder, os.path.basename(tcl_lib)))

    def ignore_lib(root, items):
            ans = []
            for x in items:
                ext = os.path.splitext(x)[1]
                if (not ext and (x in ('demos', 'tzdata'))) or \
                            (ext in ('.chm', '.htm', '.txt')):
                    ans.append(x)
            return ans

    for entry in os.listdir(LIBDIR):
        if entry in ('tk{}'.format(tcl_ver), 'tcl{}'.format(tcl_ver)):
            if os.path.isdir(os.path.join(LIBDIR, entry)):
                shutil.copytree(os.path.join(LIBDIR, entry), os.path.join(py_dest, 'lib', entry), ignore=ignore_lib)


def create_site_py():
    with open(os.path.join(py_dir, 'site.py'), 'wb') as f:
        f.write(bytes(site_code))


def create_pyvenv(name):
    with open(os.path.join(temp_folder, name), 'wb') as f:
        f.write(bytes(textwrap.dedent('''\
        applocal = true
        ''')))


def create_qt_conf():
    with open(os.path.join(app_folder, 'qt.conf'), 'wb') as f:
        f.write(bytes(textwrap.dedent('''\
        [Paths]
        Prefix = .
        Libraries = .
        Plugins = .
        ''')))


def create_qt_conf2():
    with open(os.path.join(py_dest, 'bin', 'qt.conf'), 'wb') as f:
        f.write(bytes(textwrap.dedent('''\
        [Paths]
        Prefix = ../../
        Libraries = .
        Plugins = .
        ''')))


def copy_strip_qt5():
    for lib in QT_DLLS:
        name = os.path.join(QT_PREFIX, 'lib', lib)
        shutil.copy2(name, app_folder)
        subprocess.check_call(['strip', '--strip-unneeded', os.path.join(app_folder, lib)])
        # Set RPATH for Qt5 shared libraries to root lib dir
        set_rpath(os.path.join(app_folder, lib))


def copy_strip_icu(ver='55'):
    iculibs = glob.glob('{}/libicu*.so.{}'.format(LIBDIR, ver))
    for lib in iculibs:
        shutil.copy2(lib, app_folder)
        subprocess.check_call(['strip', '--strip-unneeded', os.path.join(app_folder, os.path.basename(lib))])
        # Set RPATH for ICU shared libraries to root lib dir
        set_rpath(os.path.join(app_folder, os.path.basename(lib)))


def copy_strip_qt_plugins():
    qt_plugins_dir = os.path.join(QT_PREFIX, 'plugins')
    for plugin in QT_PLUGINS:
        dest_folder = os.path.join(app_folder, plugin)
        os.mkdir(dest_folder)
        libnames = glob.glob('{}/lib*.so'.format(os.path.join(qt_plugins_dir, plugin)))
        for f in libnames:
            shutil.copy2(f, dest_folder)
            subprocess.check_call(['strip', '--strip-unneeded', os.path.join(dest_folder, os.path.basename(f))])
            set_rpath(os.path.join(dest_folder, os.path.basename(f)), depth=2)


def copy_resource_files():
    resource_dir = os.path.join(SIGIL_SRC_DIR, 'src', 'Resource_Files')

    # Copy the translation qm files
    trans_dir = os.path.join(build_dir(), 'src')
    dest_folder = os.path.join(app_folder, 'translations')
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    filenames = glob.glob('{}/*.qm'.format(trans_dir))
    for filename in filenames:
        shutil.copy2(filename, dest_folder)

    # Copy the hunspell dictionary files
    dict_dir = os.path.join(resource_dir, 'dictionaries')
    dest_folder = os.path.join(app_folder, 'hunspell_dictionaries')
    shutil.copytree(dict_dir, dest_folder)

    # Copy the MathJax.js file
    mathjax_file = os.path.join(resource_dir, 'polyfills', "MathJax.js")
    dest_folder = os.path.join(app_folder, 'polyfills')
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    shutil.copy2(mathjax_file, dest_folder)

    # plugin launcher files
    launcher_dir = os.path.join(resource_dir, 'plugin_launchers', 'python')
    dest_folder = os.path.join(app_folder, 'plugin_launchers', 'python')
    shutil.copytree(launcher_dir, dest_folder)

    # Copy the python3lib
    python3lib_dir = os.path.join(resource_dir, 'python3lib')
    dest_folder = os.path.join(app_folder, 'python3lib')
    shutil.copytree(python3lib_dir, dest_folder)

    # Copy the example files
    ex_dir = os.path.join(resource_dir, 'examples')
    dest_folder = os.path.join(app_folder, 'examples')
    shutil.copytree(ex_dir, dest_folder)


def copy_libs_bins():
    lib_src_dir = os.path.join(build_dir(), 'lib')
    bin_src_dir = os.path.join(build_dir(), 'bin')

    for lib in ['libhunspell.so', 'libsigilgumbo.so']:
        shutil.copy2(os.path.join(lib_src_dir, lib), app_folder)
        subprocess.check_call(['strip', '--strip-unneeded', os.path.join(app_folder, lib)])
        set_rpath(os.path.join(app_folder, lib))

    if os.path.exists(os.path.join(lib_src_dir, 'libxml2.so.2')):
        shutil.copy2(os.path.join(lib_src_dir, 'libxml2.so.2'), app_folder)
        subprocess.check_call(['strip', '--strip-unneeded', os.path.join(app_folder, 'libxml2.so.2')])
        set_rpath(os.path.join(app_folder, 'libxml2.so.2'))
    shutil.copy2(os.path.join(bin_src_dir, 'sigil'), app_folder)
    subprocess.check_call(['strip', '--strip-unneeded', os.path.join(app_folder, 'sigil')])
    set_rpath(os.path.join(app_folder, 'sigil'))


def copy_misc_files():
    resource_dir = os.path.join(SIGIL_SRC_DIR, 'src', 'Resource_Files')
    # Copy the Changelog
    shutil.copy2(os.path.join(SIGIL_SRC_DIR, 'ChangeLog.txt'), app_folder)
    # Copy the license file
    shutil.copy2(os.path.join(SIGIL_SRC_DIR, 'COPYING.txt'), app_folder)
    # Copy the icon file (used on Linux for the application icon)
    shutil.copy2(os.path.join(resource_dir, 'icon', 'app_icon_48.png'), temp_folder)
    # Copy the desktop file (used on Linux for the application settings)
    shutil.copy2(os.path.join(resource_dir, 'freedesktop', 'sigil.desktop'), temp_folder)


def copy_strip_extra_manifest(manifest_file):
    with open(manifest_file, 'r') as f:
        for line in f:
            filepath = line.strip()
            if len(filepath) and not filepath.startswith('#'):
                if not is64bit:
                    filepath = filepath.replace('x86_64-', 'i386-')
                shutil.copy2(filepath, app_folder)
                try:
                    os.chmod(os.path.join(app_folder, os.path.basename(filepath)), 0o755)
                    subprocess.check_call(['strip', '--strip-unneeded', os.path.join(app_folder, os.path.basename(filepath))])
                    set_rpath(os.path.join(app_folder, os.path.basename(filepath)))
                except:
                    pass


def create_launcher(filename, inst_dir, perms):
    with open(os.path.join(temp_folder, filename), 'wb') as f:
        f.write(bytes(launcher_bash.format(inst_dir)))
    os.chmod(os.path.join(temp_folder, filename), perms)


def create_setup():
    with open(os.path.join(temp_folder, 'setup.sh'), 'wb') as f:
        f.write(bytes(setup_bash.format(BASE_INSTALL_DIR)))
    os.chmod(os.path.join(temp_folder, 'setup.sh'), 0o744)


def create_uninstall(filename, paths):
    with open(os.path.join(temp_folder, filename), 'wb') as f:
        f.write(bytes(uninstall_script.format(**paths)))
    os.chmod(os.path.join(temp_folder, filename), 0o755)


def create_bytecompile():
    with open(os.path.join(build_dir(), PY_COMPILE_FILE), 'wb') as f:
        f.write(bytes(compile_code.format(py_dir)))


def main():
    copy_pylib()
    copy_python()
    copy_site_packages(site_packages, site_dest)

    # Set RPATH for shared libraries in site-packages directory to root lib dir
    root = os.path.join(py_dir, 'site-packages')
    for item in os.listdir(root):
        f = os.path.join(root, item)
        if os.path.isfile(f) and os.path.splitext(f)[1] == '.so':
            set_rpath(f, depth=5)
    # Set RPATH for shared libraries in lxml module to root lib dir
    root = os.path.join(py_dir, 'site-packages', 'lxml')
    for item in os.listdir(root):
        f = os.path.join(root, item)
        if os.path.isfile(f) and os.path.splitext(f)[1] == '.so':
            set_rpath(f, depth=6)
    # Set RPATH for shared libraries in PIL module to root lib dir
    root = os.path.join(py_dir, 'site-packages', 'PIL')
    for item in os.listdir(root):
        f = os.path.join(root, item)
        if os.path.isfile(f) and os.path.splitext(f)[1] == '.so':
            set_rpath(f, depth=6)

    create_site_py()
    copy_tcltk()

    copy_strip_qt5()
    copy_strip_icu(ver=icu_ver)
    copy_strip_qt_plugins()
    copy_resource_files()
    copy_libs_bins()
    copy_misc_files()
    if os.path.exists(EXTRA_MANIFEST):
        copy_strip_extra_manifest(EXTRA_MANIFEST)
    create_launcher('user_sigil.sh', '~/opt/{}'.format(BASE_INSTALL_DIR), 0o755)
    create_launcher('system_sigil.sh', '/opt/{}'.format(BASE_INSTALL_DIR), 0o755)
    create_pyvenv('user_pyvenv.cfg')
    create_pyvenv('system_pyvenv.cfg')
    create_qt_conf()
    create_qt_conf2()
    create_setup()
    create_uninstall('remove_sigil_root', root_paths)
    create_uninstall('remove_sigil_user', user_paths)
    # Create python script to be run by the custom-built python3 (to precompile python modules).
    # Will be run by the parent script - build_sigil.py.
    create_bytecompile()


if __name__ == '__main__':
    main()
