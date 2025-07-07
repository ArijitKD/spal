# spal
Scripts Package Assembler for Linux. Helps assemble your executable scripts into distributable packages.

# Platform support

- Currently supports `.deb` packages only
- Supported package managers: `pkg`, `apt`.

### Commands to be supported:

```
spal {-g | --generate-buildcfg} \
    --pkgmgr <pkg-mgr> \
    --dist <dist> \
    --comp <comp> \
    --shellscript <shell-script> \
    --control <control-file> \
    [--srcroot <src-rootdir> [--exclude <file-1> <file-2> ...]] \
    [--man <man-filename>] \
    [--copyright <copyright-filename>] \
    [--outfile <output-filename>]

spal [{-k | --keep-buildtree}] <build-cfg> <out-dir>

spal [{-h | --help}]

spal {-v | --version}
```
