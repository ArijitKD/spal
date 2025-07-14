#!/usr/bin/env python3

# File: ./spal.py
#
# spal - Scripts Package Assembler for Linux. Helps assemble your executable
# scripts into distributable packages.
#
#
# Copyright (C) 2025-Present Arijit Kumar Das <arijitkdgit.official@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import subprocess
import sys
import os
import shutil
import gzip


CFG_TEMPLATE = {
    "pkgmgr"       : "",
    "dist"         : "",
    "comp"         : "",
    "shellscript"  : "",
    "sources"      : [],
    "man"          : "",
    "control"      : "",
    "copyright"    : ""
}

SUPPORTED_PACKAGE_MANAGERS = ["apt", "pkg"]
USR_DIR = {
    "apt" : "usr",
    "pkg" : "data/data/com.termux/files/usr"
}

VERSION = "1.1"
VERSION_TEXT = \
f'''spal {VERSION}
Copyright (c) 2025-Present Arijit Kumar Das <arijitkdgit.official@gmail.com>
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This program is free software; you may redistribute it under the terms of
the GNU General Public License version 3 or later.
This program has absolutely no warranty.'''

HELP_TEXT = \
f'''Help for spal (version {VERSION})

spal: Scripts Package Assembler for Linux. Helps assemble executable scripts
into distributable packages. Currently supports building .deb packages only.
''' \
'''
#1 Possible usage patterns:
  1. spal {-g | --generate-buildcfg} \\
         --pkgmgr <pkg-mgr> \\
         --dist <dist> \\
         --comp <comp> \\
         --shellscript <shell-script> \\
         --control <control-file> \\
         [--srcroot <src-rootdir> [--exclude <file-1> ... <file-n>]] \\
         [--man <man-filename>] \\
         [--copyright <copyright-filename>] \\
         [--outfile <output-filename>]
  2. spal [{-k | --keep-buildtree}] [{-s | --debstdname}] <buildcfg> <outdir>
  3. spal [{-h | --help}]
  4. spal {-v | --version}

#2 Meanings of notations used above:
  - <...>       :  A mandatory value for the preceding option. A
                   value must not contain a space anywhere.

  - {... | ...} :  A shorthand and full name for the same option.

  - [...]       :  Non-mandatory options.
  
  - [... [...]] :  Two non-mandatory options, but the inner option
                   may not be specified without the outer option.
'''\
f'''
#3 Available options:
  1. -g, --generate-buildcfg  :  Specify to generate a build config file. See
                                 section #1 pattern (1) for usage.

  2. --pkgmgr                 :  Specify the package manager to be used for the
                                 build process. Currently supported package
                                 managers are: {SUPPORTED_PACKAGE_MANAGERS}.

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
'''

ERR_FILE_NOT_FOUND = -2
ERR_UNSUPPORTED_PACKAGE_MANAGER = -3
ERR_NO_PACKAGE_NAME = -4
ERR_NO_VERSION_STRING = -5
ERR_SRCROOT_UNSPECIFIED = -6
ERR_SUBPROCESS_FAILED = -7
ERR_SRCROOT_IS_CWD = -8

errno: int = 0
errdesc: str = ""

cfgfile: str = ""


def get_last_error() -> tuple:
    global errdesc, errno
    last_errdesc: str = errdesc
    last_errno: int = errno
    if (errdesc != ""):
        errdesc = ""
    if (errno != 0):
        errno = 0
    return (last_errno, last_errdesc)


def get_package_name(control_text: str) -> str:
    global errno, errdesc
    lines: list = control_text.split('\n')
    package: str = ""
    for line in lines:
        line = line.strip()
        if (line.startswith("Package:")):
            package = line[line.index(':') + 1 :].strip()
    if (package == ""):
        errno = ERR_NO_PACKAGE_NAME
        errdesc = "Control text has no package name"
    return package


def get_version(control_text: str) -> str:
    global errno, errdesc
    lines: list = control_text.split('\n')
    version: str = ""
    for line in lines:
        line = line.strip()
        if (line.startswith("Version:")):
            version = line[line.index(':') + 1 :].strip()
    if (version == ""):
        errno = ERR_NO_VERSION_STRING
        errdesc = "Control text has no version string"
    return version


def getcfg(cfg: str) -> dict:
    '''
    Returns the build configuration from the configuration file a.k.a cfg.
    If the file is not found, sets errno and errdesc and returns an empty
    dictionary.
    '''
    global errno, errdesc
    if (not os.path.isfile(cfg)):
        errno = ERR_FILE_NOT_FOUND
        errdesc = f"File \"{cfg}\" not found."
        return {}

    buildcfg: dict = CFG_TEMPLATE.copy()
    with open(cfg) as cfgfile:
        lines: list = cfgfile.readlines()
        total_lines: int = len(lines)
        i: int = 0
        while (i < total_lines):
            line = lines[i].strip()

            if (line == "[PACKAGE-MANAGER]" and
                i + 1 != total_lines):
                buildcfg["pkgmgr"] = lines[i + 1].strip()

            elif (line == "[DISTRIBUTION]" and
                i + 1 != total_lines):
                buildcfg["dist"] = lines[i + 1].strip()

            elif (line == "[COMPONENT]" and
                i + 1 != total_lines):
                buildcfg["comp"] = lines[i + 1].strip()

            elif (line == "[SHELLSCRIPT]" and
                i + 1 != total_lines):
                j = i + 1
                while (lines[j].strip() != "[END]" and
                    j + 1 != total_lines):
                    buildcfg["shellscript"] += lines[j]
                    j += 1
                i = j + 1
                continue

            elif (line == "[SOURCES]" and
                i + 1 != total_lines):
                j = i + 1
                while (lines[j].strip() != "[END]" and
                    j + 1 != total_lines):
                    buildcfg["sources"].append(lines[j].strip())
                    j += 1
                i = j + 1
                continue

            elif (line == "[CONTROL]" and
                i + 1 != total_lines):
                j = i + 1
                while (lines[j].strip() != "[END]" and
                    j + 1 != total_lines):
                    buildcfg["control"] += lines[j]
                    j += 1
                i = j + 1
                continue

            elif (line == "[MAN]" and
                i + 1 != total_lines):
                j = i + 1
                while (lines[j].strip() != "[END]" and
                    j + 1 != total_lines):
                    buildcfg["man"] += lines[j]
                    j += 1
                i = j + 1
                continue

            elif (line == "[COPYRIGHT]" and
                i + 1 != total_lines):
                j = i + 1
                while (lines[j].strip() != "[END]" and
                    j + 1 != total_lines):
                    buildcfg["copyright"] += lines[j]
                    j += 1
                i = j + 1
                continue

            i += 1

    return buildcfg


def get_rootdir(buildcfg: str, outdir: str) -> str:
    '''
    Get the root directory of the build tree. Sets errno and errdesc if an
    unsupported package manager is specified in the build configuration.
    '''
    global errno, errdesc
    pkgmgr: str = buildcfg["pkgmgr"]
    if (pkgmgr not in SUPPORTED_PACKAGE_MANAGERS):
        errno = ERR_UNSUPPORTED_PACKAGE_MANAGER
        errdesc = f"Unsupported package manager \"{pkgmgr}\"."
        return ""
    package: str = get_package_name(buildcfg["control"])
    version: str = get_version(buildcfg["control"])
    if ("" in (package, version)):
        return ""
    dist: str = buildcfg["dist"]
    comp: str = buildcfg["comp"]
    rootdir: str = os.path.join(
                        outdir, f"{package}_{version}_all.{pkgmgr}.{dist}.{comp}")
    return rootdir


def get_usrdir(buildcfg: str, outdir: str) -> str:
    rootdir: str = get_rootdir(buildcfg, outdir)
    if (rootdir == ""):
        return ""
    pkgmgr: str = buildcfg["pkgmgr"]
    usrdir: str = os.path.join(rootdir, USR_DIR[pkgmgr])
    return usrdir


def mk_buildtree(buildcfg: dict, outdir: str) -> int:
    '''
    Creates the build tree for the building the package. Returns -1 if the root
    directory is empty (an error in call to get_rootdir()).
    '''
    rootdir: str = get_rootdir(buildcfg, outdir)
    if (rootdir == ""):
        return -1
    usrdir: str = get_usrdir(buildcfg, outdir)
    package: str = get_package_name(buildcfg["control"])
    os.makedirs(os.path.join(rootdir, "DEBIAN"), 0o755, True)
    os.makedirs(os.path.join(usrdir, "bin"), 0o755, True)
    if (buildcfg["sources"] != ""):
        os.makedirs(os.path.join(usrdir, "lib", package), 0o755, True)
    if (buildcfg["copyright"] != ""):
        os.makedirs(os.path.join(
                        usrdir, "share", "doc", package), 0o755, True)
    if (buildcfg["man"] != ""):
        os.makedirs(os.path.join(
                        usrdir, "share", "man", "man1"), 0o755, True)
    return 0


def mk_control(buildcfg: dict, outdir: str) -> int:
    '''
    Creates the control file, assuming the "DEBIAN" directory to be present in
    the root directory. Returns -1 if the root directory is empty (an error in
    call to get_rootdir()).
    '''
    rootdir: str = get_rootdir(buildcfg, outdir)
    if (rootdir == ""):
        return -1
    with open(os.path.join(rootdir, "DEBIAN", "control"), 'w') as control:
        control.write(buildcfg["control"])
    return 0


def mk_copyright(buildcfg: dict, outdir: str) -> int:
    '''
    Creates the copyright file, assuming the parent directories to be present in
    the root directory. Returns -1 if the root directory is empty (an error in
    call to get_rootdir()).
    '''
    usrdir: str = get_usrdir(buildcfg, outdir)
    if (usrdir == ""):
        return -1
    docdir: str = os.path.join(usrdir, "share", "doc")
    package: str = get_package_name(buildcfg["control"])

    if (not os.path.isdir(os.path.join(docdir, package))):
        return 0

    copyrightfile: str = os.path.join(docdir, package, "copyright")
    with open(copyrightfile, 'w') as copyright:
        copyright.write(buildcfg["copyright"])
    return 0


def mk_shwrapper(buildcfg: dict, outdir: str) -> int:
    '''
    Creates the wrapper shellscript, assuming the parent directories to be present in
    the root directory. Returns -1 if the root directory is empty (an error in
    call to get_rootdir()).
    '''
    usrdir: str = get_usrdir(buildcfg, outdir)
    if (usrdir == ""):
        return -1
    bindir: str = os.path.join(usrdir, "bin")
    package: str = get_package_name(buildcfg["control"])
    with open(os.path.join(bindir, package), 'w') as shellscript:
        shellscript.write(buildcfg["shellscript"])
    os.chmod(os.path.join(bindir, package), 0o755)
    return 0


def mk_man(buildcfg: dict, outdir: str) -> int:
    '''
    Creates the man file and gzips it, assuming the parent directories to be present
    in the root directory. Returns -1 if the root directory is empty (an error in
    call to get_rootdir()).
    '''
    usrdir: str = get_usrdir(buildcfg, outdir)
    if (usrdir == ""):
        return -1
    man1dir: str = os.path.join(usrdir, "share", "man", "man1")

    if (not os.path.isdir(man1dir)):
        return 0

    package: str = get_package_name(buildcfg["control"])

    gzman1file: str = os.path.join(man1dir, f"{package}.1") + ".gz"
    gzman1 = gzip.GzipFile(
                filename = gzman1file,
                mode = "wb",
                compresslevel = 9,
                mtime = 0
            )
    gzman1.write(buildcfg["man"].encode())
    gzman1.close()
    return 0


def cp_sources(buildcfg: dict, outdir: str) -> int:
    sources: list = buildcfg["sources"]
    if (sources == []):
        return 0
    usrdir: str = get_usrdir(buildcfg, outdir)
    if (usrdir == ""):
        return -1
    package: str = get_package_name(buildcfg["control"])
    destroot: str = os.path.join(usrdir, "lib", package)
    rootdir: str = get_rootdir(buildcfg, outdir)
    for src in sources:
        dest: str = os.path.join(destroot, os.path.basename(src))
        if (os.path.isdir(src)):
            shutil.copytree(src, dest, dirs_exist_ok = True)
        else:
            shutil.copy2(src, dest)
    return 0


def parse_args_gencfg(args: list) -> dict:
    if (args == [] or args[0] not in {"-g", "--generate-buildcfg"}):
        return {}
    compulsory_args: list = [
        "pkgmgr",
        "dist",
        "comp",
        "shellscript",
        "control"
    ]
    optional_args: list = [
        "srcroot",
        "exclude",
        "man",
        "copyright",
        "outfile"
    ]
    parsed_args: dict = {}
    # Avoid KeyError if absent
    for arg in (compulsory_args + optional_args):
        if (arg == "exclude"):
            parsed_args[arg] = []
        else:
            parsed_args[arg] = ""
    i: int = 1
    arg_count: int = len(args)
    while (i < arg_count):
        arg: str = args[i]
        if (arg.startswith("--") and (i + 1 < arg_count)):
            j: int = i + 1
            arg = arg.lstrip("--")
            if (arg == "exclude"):
                while (j < arg_count and not args[j].startswith("--")):
                    parsed_args[arg].append(args[j])
                    j += 1
            else:
                if (args[j].startswith("--")): return {}
                else: parsed_args[arg]= args[j]
            i = j
        else:
            i += 1
    for arg in compulsory_args:
        if (parsed_args[arg] == ""):
            return {}
    for arg in parsed_args:
        if (arg not in (compulsory_args + optional_args)):
            return {}
    return parsed_args


def parse_args_build(args: list) -> list:
    parsed_args: dict = {}

    if (len(args) > 4):
        return {}

    if (args[-1].startswith("-") or
        args[-2].startswith("-")):
        return {}

    parsed_args["outdir"] = args[-1]
    parsed_args["buildcfg"] = args[-2]
    parsed_args["keep-buildtree"] = False
    parsed_args["use-debstdname"] = False

    valid_options: set = {"-k", "--keep-buildtree", "-s", "--use-debstdname"}
    for arg in args[0:-2]:
        if (arg in {"-k", "--keep-buildtree"}):
            parsed_args["keep-buildtree"] = True
        elif (arg in {"-s", "--use-debstdname"}):
            parsed_args["use-debstdname"] = True
        else:
            return {}

    return parsed_args


def mk_cfg(parsed_args: dict) -> int:
    global cfgfile, errno, errdesc
    cfgfile = os.path.basename(parsed_args["shellscript"]) + "." + \
        parsed_args["pkgmgr"] + "." + parsed_args["dist"] + "." + \
        parsed_args["comp"] + ".spalcfg"
    if (parsed_args["outfile"] != ""):
        cfgfile = parsed_args["outfile"]
        cfgfile += ".spalcfg" if not cfgfile.endswith(".spalcfg") else ""

    shfile: str = parsed_args["shellscript"]
    if (not os.path.isfile(shfile)):
        errno = ERR_FILE_NOT_FOUND
        errdesc = f"File \"{shfile}\" not found."
        return -1

    ctrlfile: str = parsed_args["control"]
    if (not os.path.isfile(ctrlfile)):
        errno = ERR_FILE_NOT_FOUND
        errdesc = f"File \"{ctrlfile}\" not found."
        return -1

    srcrootdir: str = parsed_args["srcroot"]
    if (srcrootdir != "" and not os.path.isdir(srcrootdir)):
        errno = ERR_FILE_NOT_FOUND
        errdesc = f"Source root \"{srcrootdir}\" not found."
        return -1

    if (srcrootdir == "."):
        errno = ERR_SRCROOT_IS_CWD
        errdesc = f"Source root cannot be same as current working directory."
        return -1

    excluded_files: list = parsed_args["exclude"]
    if (srcrootdir == "" and excluded_files != []):
        errno = ERR_SRCROOT_UNSPECIFIED
        errdesc = f"Attempted to exclude files without specifying source root."
        return -1

    manfile: list = parsed_args["man"]
    if (manfile != "" and not os.path.isfile(manfile)):
        errno = ERR_FILE_NOT_FOUND
        errdesc = f"Man file \"{manfile}\" not found."
        return -1

    copyrightfile: list = parsed_args["copyright"]
    if (copyrightfile != "" and not os.path.isfile(copyrightfile)):
        errno = ERR_FILE_NOT_FOUND
        errdesc = f"Copyright file \"{copyrightfile}\" not found."
        return -1

    spalconfig = open(cfgfile, 'w')
    spalconfig.writelines([
        "[PACKAGE-MANAGER]\n",
        parsed_args["pkgmgr"] + "\n",
        "[END]\n",
        "\n\n",
        "[DISTRIBUTION]\n",
        parsed_args["dist"] + "\n",
        "[END]\n",
        "\n\n",
        "[COMPONENT]\n",
        parsed_args["comp"] + "\n",
        "[END]\n",
        "\n\n"
    ])

    shellscript: list = []
    with open(shfile) as file:
        shellscript = file.readlines()
    spalconfig.writelines([
        "[SHELLSCRIPT]\n"
    ] + shellscript + ["[END]\n", "\n\n"])
    
    control: list = []
    with open(ctrlfile) as file:
        control = file.readlines()
    spalconfig.writelines([
        "[CONTROL]\n"
    ] + control + ["[END]\n", "\n\n"])

    if (srcrootdir != ""):
        spalconfig.write("[SOURCES]\n")
        for src in os.listdir(srcrootdir):
            if (src not in excluded_files):
                spalconfig.write(
                    os.path.join(srcrootdir, src) + "\n"
                )
        spalconfig.writelines(["[END]\n", "\n\n"])

    if (manfile != ""):
        man: list = []
        with open(manfile) as file:
            man = file.readlines()
        spalconfig.writelines([
            "[MAN]\n"
        ] + man + ["[END]\n", "\n\n"])

    if (copyrightfile != ""):
        copyright: list = []
        with open(copyrightfile) as file:
            copyright = file.readlines()
        spalconfig.writelines([
            "[COPYRIGHT]\n"
        ] + copyright + ["[END]\n", "\n\n"])

    spalconfig.close()
    return 0


def build_package(rootdir: str, buildcfg = {}) -> str:
    build_proc = subprocess.run(
        ["dpkg", "--build", rootdir],
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        text = True
    )

    debname: str = rootdir + ".deb"
    if (build_proc.returncode != 0):
        errno = ERR_SUBPROCESS_FAILED
        errdesc = build_proc.stdout
        return ""

    if (buildcfg != {}):
        outdir: str = os.path.dirname(rootdir)
        debdir_basename: str = buildcfg["pkgmgr"] + "." + \
            buildcfg["dist"] + "." + buildcfg["comp"]
        debdir: str = os.path.join(outdir, debdir_basename)
        package: str = get_package_name(buildcfg["control"])
        version: str = get_version(buildcfg["control"])
        old_deb: str = rootdir + ".deb"
        new_deb: str = os.path.join(debdir, package + "_" + \
            version + "_all.deb")
        os.makedirs(debdir, exist_ok = True)
        os.rename(old_deb, new_deb)
        debname = new_deb

    return debname


def show_help() -> None:
    print(HELP_TEXT)


def show_version() -> None:
    print(VERSION_TEXT)


def main() -> None:
    args: list = sys.argv[1:]

    if (args == [] or args[0] in ("-h", "--help")):
        show_help()
        sys.exit(0)
    
    if (args[0] in ("-v", "--version")):
        show_version()
        sys.exit(0)

    parsed_args_gencfg: dict = parse_args_gencfg(args)
    parsed_args_build: dict = parse_args_build(args)

    if (parsed_args_gencfg == {} and parsed_args_build == {}):
        print(
            "spal: Invalid arguments or combination of arguments.\n"
            "Use \"spal -h\" to view help."
        )
        sys.exit(1)

    if (parsed_args_gencfg != {}):
        if (mk_cfg(parsed_args_gencfg) != 0):
            error: tuple = get_last_error()
            print(
                f"spal: Error in generating build config (errorcode: {error[0]}).\n"
                f"Error message:\n{error[1]}"
            )
            sys.exit(1)
        else:
            print(cfgfile)
            sys.exit(0)
    if (parsed_args_build != {}):
        buildcfg = getcfg(parsed_args_build["buildcfg"])
        outdir: str = parsed_args_build["outdir"]

        if (buildcfg == {}):
            error: tuple = get_last_error()
            print(
                f"spal: Error in pre-build process (errorcode: {error[0]})\n"
                f"Error message:\n{error[1]}"
            )
            sys.exit(1)

        rootdir: str = get_rootdir(buildcfg, outdir)

        calls: list = [
            mk_buildtree,
            mk_control,
            mk_copyright,
            mk_shwrapper,
            mk_man,
            cp_sources
        ]
        for call in calls:
            if (call(buildcfg, outdir) != 0):
                error: tuple = get_last_error()
                print(
                    f"spal: Error in pre-build process (errorcode: {error[0]})\n"
                    f"Error message:\n{error[1]}"
                )
                sys.exit(1)

        debname: str = ""
        if (parsed_args_build["use-debstdname"]):
            debname = build_package(rootdir, buildcfg)
        else:
            debname = build_package(rootdir)

        if (debname == ""):
            error: tuple = get_last_error()
            print(
                f"spal: Error in building package (errorcode: {error[0]}).\n"
                f"Error message:\n{error[1]}"
            )
            sys.exit(1)
        else:
            print(debname)

        if (not parsed_args_build["keep-buildtree"]):
            shutil.rmtree(rootdir)

        sys.exit(debname == "")
                

if (__name__ == "__main__"):
    main()

