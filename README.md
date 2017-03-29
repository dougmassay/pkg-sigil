Unofficial Self-Contained Sigil Package/Installer for Linux
===========================================================

<hr>

## Goal: to provide a self-contained binary installer for Sigil that works on any Linux system with a libc version of 2.19 or higher (ldd --version).


## Please note that "self-contained" does not mean portable or relocatable!!

<hr>

### NOTE: some people are reporting installer-script syntax errors when using various shells. Until I make some changes to make the shell-script more "portable," try explicitly using a bash shell to launch the installer. Using the skiplibctest argument as described in the trouble-shooting section of the INSTALL documentation (if you're certain your libc is recent enough) may work around the issue as well.

<hr>

### Read/Download [Latest Release](https://github.com/dougmassay/pkg-sigil/releases/latest)

### For instructions on downloading/installing/uninstalling this self-contained version of Sigil for Linux see [the INSTALL.md document](./INSTALL.md).

### For instuctions on how to build the self-contained Linux package/installer yourself, see [the BUILD.md document](./BUILD.md).

#### NOTE: Please do not report issues with this Sigil installer in the official Sigil issue tracker. Use [this repository's issue system instead](https://github.com/dougmassay/pkg-sigil/issues) instead. Sigil feature requests raised here will also be closed without comment.