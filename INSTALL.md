Installing this Unofficial Self-Contained Version of Sigil for Linux
=========================================================================

## Requirements
- Linux OS with GLIBC version 2.19 or higher (that's the goal, anyway). `ldd --version`
- xz-utils (the archive uses xz compression)
- I strongly recommend removing any other versions of Sigil if you're installing this package system-wide (/opt/sigil).

## Download

Download the latest installer [from here](https://github.com/dougmassay/pkg-sigil/releases/latest).

Make sure you download the correct installer for your system.

64-bit = Sigil-vX.X.X-Linux-x86_64.xz.run<br>
32-bit = Sigil-vX.X.X-Linux-x86.xz.run

## Build

Instructions to build the installer yourself [can be read here](./BUILD.md).

<hr>

## Installing

The uninstaller comes as a [Makeself](https://github.com/megastep/makeself) self-extracting/installing archive. The only requirement to run it should be xz-utils (the archive uses xz compression). If it's not already executable, make it so and launch the installer by CDing to the directory you downloaded it to and running it in a terminal. You will be told where Sigil is going to be installed and prompted to continue/cancel.

This version of Sigil can be installed in one of two ways:

### Install as root:

>`sudo ./Sigil-vX.X.X-Linux-x86(_64).xz.run`

If the Sigil installer is run as root, it will extract to a temporary directory and install the bulk of its contents to the /opt/sigil directory. The rest of the files/links to be installed are as follows:

- /usr/bin/sigil (a link to the launch script in /opt/sigil)
- /usr/share/applications/sigil.desktop
- /usr/share/pixmaps/sigil.png

Sigil can either be launched from the Desktop Environment's menu system (under Office), or by typing `sigil` at a terminal.

### Install as normal user:

>`./Sigil-vX.X.X-Linux-x86(_64).xz.run`

Some systems may be able to launch an xterm by double-clicking the installer.

With this option, Sigil can be installed entirely within the user's home directory. Handy for those who don't like running random internet scripts as root.

When the Sigil installer is run as a normal user, it will extract to a temporary directory and install the bulk of its contents to the $HOME/opt/sigil directory. The rest of the files/links to be installed are as follows:

- $HOME/bin/sigil
- $HOME/.local/share/applications/sigil.desktop
- $HOME/.icons/sigil.png

Sigil can either be launched from the Desktop Environment's menu system (under Office), or by typing `~/bin/sigil` at a terminal (or just `sigil` if $HOME/bin is in your $PATH).

### Preference Directory

This standalone version of Sigil's preference directory is being kept separate from the official version's prefs directory. You can always open it by using Edit->Preferences->Open Preferences Location from within Sigil, but it's currently the $HOME/.local/share/bundled-sigil-ebook/sigil/ directory.

### Uninstalling Sigil

An uninstall script called 'remove_sigil' gets extracted to Sigil main installation directory. Simply run it to remove Sigil from your system. You'll need to run it as root if you installed Sigil system-wide to /opt/sigil. Otherwise you can run it as a normal user.

>`sudo /opt/sigil/remove_sigil`

or

>`~/opt/sigil/remove_sigil`

The Sigil preference directory "$HOME/.local/share/bundled-sigil-ebook/sigil/" will not be removed with this script.

### Expected functionality

Everything should function exactly as the official version of Sigil with the exception of audio/video playback -- which is currently not possible with this version. You can still build an epub with audio/video components, you'll just need to use something else to preview them.

### Troubleshooting

The installer aborts if it detects a glibc version less than 2.19. If you feel the check is not reporting your glibc version correctly, you may override the check by passing the "skiplibctest" parameter to the installer. You're on own your own if Sigil doesn't work, though.

> `./Sigil-vX.X.X-Linux-x86(_64).xz.run skiplibctest`

### Advanced Makeself installer options

For those familiar with [Makeself](https://github.com/megastep/makeself), there are several arguments you can pass to any Makeself archive for various purpose. Some of those include:

- --info : Print out general information about the archive (does not extract).

- --list : List the files in the archive.

- --check : Check the archive for integrity using the embedded checksums. Does not extract the archive.

- --keep : Prevent the files to be extracted to a temporary directory from being removed after the embedded script's execution. The files will then be extracted in the current working directory and will stay here until you remove them.

- --noexec : Do not run the embedded script after extraction.

If someone wanted to manually extract the files, they should use

> `./Sigil-vX.X.X-Linux-x86(_64).xz.run --keep --noexec`

That will extract the contents of the archive (a folder named "temp_folder") to the current working directory.