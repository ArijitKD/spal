#!/usr/bin/env python3

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

ERR_FILE_NOT_FOUND = -2
ERR_UNSUPPORTED_PACKAGE_MANAGER = -3
ERR_NO_PACKAGE_NAME = -4
ERR_NO_VERSION_STRING = -5

errno: int = 0
errdesc: str = ""


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
        errdesc = f"File {cfg} not found."
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
    for arg in compulsory_args:
        parsed_args[arg] = ""   # Avoid KeyError if absent
    i: int = 1
    arg_count: int = len(args)
    while (i < arg_count):
        arg: str = args[i]
        if (arg.startswith("--") and (i + 1 < arg_count)):
            j: int = i + 1
            arg = arg.lstrip("--")
            if (arg == "exclude"):
                parsed_args[arg]: list = []
                while (j < arg_count and not args[j].startswith("--")):
                    parsed_args[arg].append(args[j])
                    j += 1
            else:
                parsed_args[arg]: str = args[j]
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
    if (len(args) == 3 and args[0] in {"-k", "--keep-buildtree"}):
        parsed_args["keep-buildtree"] = True
        parsed_args["buildcfg"] = args[1]
        parsed_args["outdir"] = args[2]
    elif (len(args) == 2 and args[0] not in {"-k", "--keep-buildtree"}):
        parsed_args["keep-buildtree"] = False
        parsed_args["buildcfg"] = args[0]
        parsed_args["outdir"] = args[1]
    return parsed_args


def mkcfg(parsed_args: dict) -> int:
    pass

def main() -> None:
    '''
    buildcfg = getcfg(sys.argv[1])
    calls: list = [
        mk_buildtree,
        mk_control,
        mk_copyright,
        mk_shwrapper,
        mk_man,
        cp_sources
    ]
    outdir: str = sys.argv[2]
    for call in calls:
        if (call(buildcfg, outdir) != 0):
            print(
                f"spal: Error in pre-build process (errorcode: {errno})\n"
                f"Error message: {errdesc}"
            )
            sys.exit(1)
    sys.exit(0)
    '''
    print (parse_args_gencfg(sys.argv[1:]))
    print (parse_args_build(sys.argv[1:]))

if (__name__ == "__main__"):
    main()

























