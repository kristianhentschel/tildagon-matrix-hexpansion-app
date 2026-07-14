from . import blit16, blit32

class TextRenderer:
  """ (not used) text renderer; text is now rendered on the hexpansion instead. """
  def __init__(self, board):
    self.board = board
    matrix = board.matrix()
    self.cols = matrix["cols"]
    self.rows = matrix["rows"]
    self.grid = matrix["grid"]
    self.buffer = [0] * len([1 for x in self.grid if x is not None])

  def render(self, text, offset=0, font="blit16"):
    BlitFont = blit16
    if font == "blit32":
      BlitFont = blit32
    dx = -offset
    for c in text:
      if dx < -1 * BlitFont.WIDTH:
        dx += BlitFont.X_ADVANCE
        continue

      print(f"Drawing '{c}' at column {dx}")
      glyph = BlitFont.get_glyph(c)
      if glyph is None:
        dx += BlitFont.X_ADVANCE
        continue
      
      shiftY = glyph >> (BlitFont.WIDTH * BlitFont.HEIGHT) & 0x03 # TODO extra bits helper fn
      # encoding is by row
      for i in range(BlitFont.HEIGHT):
        row = (8 - min(2, BlitFont.DESCENDER) - BlitFont.HEIGHT) + i + shiftY
        row_bits = glyph >> BlitFont.WIDTH * i & 0x1f # TODO mask also depends on WIDTH
        print(f"Row {row} bits: {''.join(['#' if row_bits & (0x01 << x) else ' ' for x in range(BlitFont.WIDTH)])}")
        
        # interpret bits for each column in the row
        for j in range(BlitFont.WIDTH):
          col = j
          x = (dx + col)
          if x < 0 or x >= self.cols:
            continue

          try:
            index = self.grid[row * self.cols + x]
            if index is None:
              continue
          except IndexError:
            continue

          if row_bits & (0x01 << col):
            self.buffer[index] = 255
          else:
            self.buffer[index] = 0

      dx += BlitFont.X_ADVANCE
      if dx > self.cols:
        print("reached end of display area")
        break


  def display(self):
    print("display")
    self.board.set_image(self.buffer)