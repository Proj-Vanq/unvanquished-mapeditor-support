mapeditor-support
=================

Unvanquished support files for map editors.

**These packages are work in progress and may not yet work!**

Using the support files
-----------------------

Pick the directory corresponding to your editor and merge the file hierarchy inside the `gamepack` subdirectory into its installation. Further install instructions are given in a seperate per-editor readme file.

Packages
--------

Packages are available for

* [Archlinux & Netradiant](https://aur.archlinux.org/packages/netradiant-unvanquished/)

Contributing
------------

The `src` directory contains common files, source files and export scripts that populate the editor specific directories. Files that aren't editor-specific should be maintained there. Ideally we will be able to auto-generate the entire contents of the editor directories eventually.
