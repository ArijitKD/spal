# spal
Scripts Package Assembler for Linux. Helps assemble executable scripts into distributable packages. Useful for packaging Python and/or shell scipts.

---

## Platform support

- Currently supports `.deb` packages only
- Supported package managers: `pkg` (Termux), `apt` (Debian derivatives).

---

## Installation

### Install via APT (Recommended)

You can install `spal` using the APT package manager from the official GitHub-hosted `stable` repository.

#### Step 1: Add the APT repository

- For **Termux**, run:

```bash
export TERMUX_ROOT="$HOME/../usr"
mkdir -p $TERMUX_ROOT/etc/apt/sources.list.d
echo "deb [trusted=yes arch=all] https://arijitkd.github.io/spal/packages/pkg stable main" | tee $TERMUX_ROOT/etc/apt/sources.list.d/spal.list
```

- For other **Debian-based distributions**, run:

```bash
echo "deb [trusted=yes arch=all] https://arijitkd.github.io/spal/packages/apt stable main" | sudo tee /etc/apt/sources.list.d/spal.list
```

> `trusted=yes` is used here because the repository is not signed with a GPG key.

#### Step 2: Update APT cache

- For **Termux**, run:

```bash
pkg update
```

- For other **Debian-based distributions**, run:

```bash
sudo apt update
```

#### Step 3: Install `spal`

- For **Termux**, run:

```bash
pkg install spal
```

- For other **Debian-based distributions**, run:

```bash
sudo apt install spal
```

### Installation from Releases

If you prefer, you can manually download and install the `.deb` package from the [Releases](https://github.com/ArijitKD/spal/releases) section of the GitHub repository.

#### Step 1: Download the `.deb` package

- Visit: [https://github.com/ArijitKD/spal/releases](https://github.com/ArijitKD/spal/releases)  
- Download the latest `.deb` file.

#### Step 2: Install using `dpkg`

```bash
sudo dpkg -i <spal-package-name>.deb
```

> Replace `<spal-package-name>` with the actual name of the downloaded package.

#### Step 3: Fix dependencies (if required)

```bash
sudo apt install -f
```

---

## Help section:

```
Help for spal (version 1.1)

spal: Scripts Package Assembler for Linux. Helps assemble executable scripts
into distributable packages. Currently supports building .deb packages only.

#1 Possible usage patterns:
  1. spal {-g | --generate-buildcfg} \
         --pkgmgr <pkg-mgr> \
         --dist <dist> \
         --comp <comp> \
         --shellscript <shell-script> \
         --control <control-file> \
         [--srcroot <src-rootdir> [--exclude <file-1> ... <file-n>]] \
         [--man <man-filename>] \
         [--copyright <copyright-filename>] \
         [--outfile <output-filename>]
  2. spal [{-k | --keep-buildtree}] <buildcfg> <outdir>
  3. spal [{-h | --help}]
  4. spal {-v | --version}

#2 Meanings of notations used above:
  - <...>       :  A mandatory value for the preceding option. A
                   value must not contain a space anywhere.

  - {... | ...} :  A shorthand and full name for the same option.

  - [...]       :  Non-mandatory options.
  
  - [... [...]] :  Two non-mandatory options, but the inner option
                   may not be specified without the outer option.

#3 Available options:
  1. -g, --generate-buildcfg  :  Specify to generate a build config file. See
                                 section #1 pattern (1) for usage.

  2. --pkgmgr                 :  Specify the package manager to be used for the
                                 build process. Currently supported package
                                 managers are: ['apt', 'pkg'].

  3. --dist                   :  Specify the package distribution name (e.g.,
                                 "stable").

  4. --comp                   :  Specify the package component name (e.g.,
                                 "main").

  5. --shellscript            :  Specify the main executable shell script that
                                 would put in /usr/bin.

  6. --control                :  Specify the control file for building the .deb
                                 package.

  7. --srcroot                :  Specify the root directory of the source tree,
                                 if any. Installed package puts source files at
                                 /usr/lib/<package-name>.

  8. --exclude                :  Specify the files in the source root directory
                                 that would be excluded. May be specified only
                                 when --srcroot is specified.

  9. --man                    :  Specify the man file, if any. Would appear
                                 when "man <package-name>" is used.

 10. --copyright              :  Specify the copyright file, if any.

 11. --outfile                :  Specify the file to which output build config
                                 would be written to. File extension: .spalcfg.
                                 If unspecified, the name would be:
                                 <shellscript>.<pkgmgr>.<dist>.<comp>.spalcfg.

 12. -k, --keep-buildtree     :  Specify whether to keep the build tree in the
                                 output directory after the package has been
                                 built. Build tree is removed by default.

 13. -s, --use-debstdname     :  Use the standard debian package naming scheme
                                 for the output package file
                                 (<pkg-name>_<ver>_all.deb). The package would
                                 be put in the directory:
                                 <outdir>/<pkgmgr>.<dist>.<comp>/

 14. -h, --help               :  Show this help section and exit.
 
 15. -v, --version            :  Show the version & copyright notice, then exit.

## NOTE:
  - On successful generation of build config file, spal prints the file name
    to stdout along with its path.

  - On build success, spal prints the .deb package name to stdout along with
    its path.

  - If an error occurs, relevant errorcode is displayed along with an error
    message.

```

---

## Man Page

For a condensed and structured reference, see the manual page after installation:

```bash
man spal
```

---

## TODO

- Refactor code into multiple related modules.
- Add support for various other files in a .deb package (e.g: `changelog`)

---

## Copyright and License
Copyright (c) 2025-Present Arijit Kumar Das [<arijitkdgit.official@gmail.com>](mailto:arijitkdgit.official@gmail.com)
This software is licensed under the GNU General Public License v3+.  
You may redistribute and/or modify it under the terms of the GPL.  
There is no warranty, express or implied.

For more details, see [LICENSE](./LICENSE).

---

## Contribution

Contributions, bug reports, and suggestions are welcome. Please adhere to UNIX programming principles while contributing.

---

## Bug reports

Report bugs to [arijitkdgit.official@gmail.com](mailto:arijitkdgit.official@gmail.com) or create an issue in the [Issues](https://github.com/ArijitKD/spal/issues) section.

