#!/usr/bin/env python3

#!/usr/bin/env python3

# File: ./spal.py
#
# spal - Scripts Package Assembler for Linux
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

from liblocal.errno import *

USR_DIR: dict = {
    "generic" : "usr",
    "termux" : "data/data/com.termux/files/usr"
}

CFG_TEMPLATE: dict = {
    "pkgmgr"     : "",
    "dist"       : "",
    "comp"       : "",
    "shwrapper"  : "",
    "man"        : "",
    "control"    : "",
    "copyright"  : ""
}

def getcfg(cfg: str) -> dict:
    '''
    Returns the build configuration from the configuration file a.k.a cfg.
    If the file is not found, sets errno and errdesc and returns an empty
    dictionary.
    '''
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

            elif (line == "[SHELL-WRAPPER]" and
                i + 1 != total_lines):
                j = i + 1
                while (lines[j].strip() != "[END]" and
                    j + 1 != total_lines):
                    buildcfg["shwrapper"] += lines[j]
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



buildcfg = getcfg(sys.argv[1])

for key in buildcfg:
    print (f"BEGIN {key.upper()}")
    print(buildcfg[key])
    print (f"END {key.upper()}\n")




























