#!/usr/bin/env python3

# File: ./liblocal/errno.py
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


ERR_FILE_NOT_FOUND = -2

errno: int = 0
errdesc: str = ""


def get_last_error() -> tuple:
    '''
    This is a stub implementation and may be overriden by the importer.
    Every call to this function must reset errno and errdesc, before
    returning their present values as a tuple (errno, errdesc).
    '''
    global errdesc, errno
    last_errdesc: str = errdesc
    last_errno: int = errno
    if (errdesc != ""):
        errdesc = ""
    if (errno != 0):
        errno = 0
    return (last_errno, last_errdesc)

