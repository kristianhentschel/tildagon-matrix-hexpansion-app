# Based on https://github.com/azmr/blit-fonts
# ISC License
# Copyright (c) 2018 Andrew Reece
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

X_ADVANCE = 4
DESCENDER = 1
BASELINE_OFFSET = DESCENDER + 1
HEIGHT = 5
WIDTH = 3

glyphs = [
  0x0000,0x2092,0x002d,0x5f7d,0x279e,0x52a5,0x7ad6,0x0012,
  0x4494,0x1491,0x0aba,0x05d0,0x1400,0x01c0,0x0400,0x12a4,
  0x2b6a,0x749a,0x752a,0x38a3,0x4f4a,0x38cf,0x3bce,0x12a7,
  0x3aae,0x49ae,0x0410,0x1410,0x4454,0x0e38,0x1511,0x10e3,
  0x73ee,0x5f7a,0x3beb,0x624e,0x3b6b,0x73cf,0x13cf,0x6b4e,
  0x5bed,0x7497,0x2b27,0x5add,0x7249,0x5b7d,0x5b6b,0x3b6e,
  0x12eb,0x4f6b,0x5aeb,0x388e,0x2497,0x6b6d,0x256d,0x5f6d,
  0x5aad,0x24ad,0x72a7,0x6496,0x4889,0x3493,0x002a,0xf000,
  0x0011,0x6b98,0x3b79,0x7270,0x7b74,0x6750,0x95d6,0xb9ee,
  0x5b59,0x6410,0xb482,0x56e8,0x6492,0x5be8,0x5b58,0x3b70,
  0x976a,0xcd6a,0x1370,0x38f0,0x64ba,0x3b68,0x2568,0x5f68,
  0x54a8,0xb9ad,0x73b8,0x64d6,0x2492,0x3593,0x03e0,
]

def get_glyph(char):
  index = ord(char) - ord(' ')
  if index > len(glyphs) or index < 0:
    return None

  return glyphs[index]

def get_char(char):
  glyph = get_glyph[char]

  cols = [0x00] * 5
  
  shiftY = glyph >> 15 & 0x01
  # encoding is by row
  for i in range(HEIGHT):
    row = glyph >> WIDTH * i & 0x03
    
    # interpret bits for each column in the row
    for j in range(7):
      if row & (0x01 << j):
        cols[j] |= i + shiftY

  return cols