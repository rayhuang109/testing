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

from struct import pack
from math import ceil
from urllib.request import urlopen

# reference: https://www.ptt.cc/bbs/Liu/M.1164374563.A.41C.html

#with urlopen('https://boshiamy.com/hliu/liu-uni.js') as f:
#    table_def = f.read().decode().replace('var ', '').replace(';', '')
with open('liu-uni.js', 'r') as f:
    table_def = f.read().replace('var ', '').replace(';', '')
eval(compile(table_def, '<string>', 'exec'))

with open("liu-uni.tab", "wb") as f:

    # first 2-byte * 32*32, table index, in little-endian
    char_count = 0
    for c in [len("".join(TableWord[i])) for i in range(len(TableWord))]:
        f.write(pack('H', char_count))
        char_count += c

    # 2-byte, total characters, in little-endian
    f.write(pack('H', char_count))

    # 2-bit * char_count, MSB 2-bit of each char, in big-endian
    all_char = "".join(list(map("".join, TableWord)))
    for chunk in [all_char[i:i+4] for i in range(0, len(all_char), 4)]:
        o = 0
        for (i, c) in enumerate(chunk):
            o |= (ord(c) >> 14) << (6-i*2)
        f.write(pack('B', o))

    # 1-bit * char_count, unknown
    f.write(bytearray(ceil(char_count/8)))

    # 1-bit * char_count, is_simplest_keycode
    f.write(bytearray(ceil(char_count/8)))

    # 3-byte * char_count, {key3[4:0], key4[4:0], char[13:0]} in big-endian
    for (i, ent) in enumerate(TableIndex):
        if len(ent) == 0:
            continue
        for (j, key34) in enumerate(ent):
            for c in TableWord[i][j]:
                o = (key34 << 14) | (ord(c) & 0x3fff)
                f.write(pack('>I', o)[1:4])
