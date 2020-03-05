#!/usr/bin/env python3
# Copyright 2020 Raymond Huang <rayhuang109@outlook.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import re
from math import ceil
from struct import pack
from functools import cmp_to_key
from urllib.request import urlopen

# reference: https://www.ptt.cc/bbs/Liu/M.1164374563.A.41C.html

keycode= " abcdefghijklmnopqrstuvwxyz,.'[]"
table_def = []

def cmp_by_keycode(a, b):
    if len(a) == 0 and len(b) == 0:
        return 0
    elif len(a) == 0 and len(b):
        return -1
    elif len(a) and len(b) == 0:
        return 1
    else:
        ret = keycode.index(a[0]) - keycode.index(b[0])
        if ret != 0:
            return ret
        else:
            return cmp_by_keycode(a[1:], b[1:])

# noseeing-12.tar.gz
with open('noseeing.cin', 'r') as f:
    raw_table = f.read().strip().split('\n')

started = False
for line in raw_table:

    if not started:
        if line.startswith('%chardef begin'):
            started = True
        continue
    elif line.startswith('%chardef end'):
        break

    # remove commline
    line = re.sub('\s*#.*$', '', line)
    if len(line) == 0:
        continue

    try:
        key, char = re.split("\s+", line)
    except:
        continue

    if len(char) > 1 or ord(char) > 0xffff:
        continue

    if len(key) > 4:
        key = key[0:4]
    elif len(key) < 4:
        key = key + ' '*(4-len(key))

    table_def.append((key, char))

table_def.sort(key=lambda x: cmp_to_key(cmp_by_keycode)(x[0]))

with open("liu-uni.tab", "wb") as f:

    # first 2-byte * 32*32, table index, in little-endian
    i = 0
    updated = False
    char_idx = 0
    char_count = len(table_def)
    while i < 1024 and char_idx < char_count:
        k1, k2 = divmod(i, 32)
        if keycode[k1] == table_def[char_idx][0][0] and\
                keycode[k2] == table_def[char_idx][0][1]:
            if not updated:
                f.write(pack('H', char_idx))
                updated = True
            char_idx += 1
        else:
            if char_idx == 0 or not updated:
                f.write(pack('H', char_idx))
            i += 1
            updated = False
    assert char_idx == char_count

    # 2-byte, total characters, in little-endian
    f.write(pack('H', char_idx))

    # 2-bit * char_count, MSB 2-bit of each char, in big-endian
    for chunk in [table_def[i:i+4] for i in range(0, char_count, 4)]:
        o = 0
        for (i, ent) in enumerate(chunk):
            c = ent[1]
            o |= (ord(c) >> 14) << (6-i*2)
        f.write(pack('B', o))

    # 1-bit * char_count, unknown
    f.write(bytearray(ceil(char_count/8)))

    # 1-bit * char_count, is_simplest_keycode
    f.write(bytearray(ceil(char_count/8)))

    # 3-byte * char_count, {key3[4:0], key4[4:0], char[13:0]} in big-endian
    for k, c in table_def:
        key34 = (keycode.index(k[2]) << 5) | keycode.index(k[3])
        o = (key34 << 14) | (ord(c) & 0x3fff)
        f.write(pack('>I', o)[1:4])
