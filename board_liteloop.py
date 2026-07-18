from system.hexpansion.config import HexpansionConfig
from system.hexpansion.header import HexpansionHeader
from .board import Board
import math

ADDRESS = 0x20

NUM_LEDS = 156
REG_PATTERN_INDEX = 0x37
REG_DIRECT_CONTROL = 0x50

class LiteLoopBoard (Board):
  def __init__(self, config: HexpansionConfig, header: HexpansionHeader):
    super().__init__(config, header)

  def set_pattern(self, pattern_index):
    # turn off pattern and set direct control all off
    self.set_all(0)

    # select pattern
    self.i2c.writeto_mem(ADDRESS, REG_PATTERN_INDEX, bytes([pattern_index]))

    # disable direct control to re-enable pattern
    self.i2c.writeto_mem(ADDRESS, REG_DIRECT_CONTROL, bytes([0]))

  def set_default_pattern(self):
    self.set_pattern(2)

  def set_all(self, value):
    """ Set all LEDs to the same constant value """
    self.i2c.writeto_mem(ADDRESS, REG_DIRECT_CONTROL, bytes([0x01] + [value] * NUM_LEDS))

  @staticmethod
  def pack_on_off_image(image):
    """ Pack a list of 156 boolean on-off values into 20 bytes to use with set_on_off_image """
    packed = [0x00] * (math.ceil(NUM_LEDS / 8))
    
    for i in range(len(packed)):
      for k in range(8):
        n = i * 8 + k
        if n < NUM_LEDS and image[n]:
          packed[i] |= 0x01 << (7 - k)

    return packed

  def set_on_off_image(self, packed):
    """ packed data is an array of 20 bytes, with each bit controlling the on-off state of one LED """
    self.i2c.writeto_mem(ADDRESS, REG_DIRECT_CONTROL, bytes([0x02] + packed[0:20]))


  def set_pwm_image(self, image):
    """ image is an array of 156 bytes, with each byte controlling the brightness level of one LED """
    self.i2c.writeto_mem(ADDRESS, REG_DIRECT_CONTROL, bytes([0x03] + image[0:NUM_LEDS]))

  def set_text(self, text, font="blit16", offset=18):
    # text contents in direct control area
    self.i2c.writeto_mem(ADDRESS, REG_DIRECT_CONTROL, bytes([0]) + text[0:NUM_LEDS - 1] + b"\0")
    
    # animation type text, and configuration for font and offset
    flags = 0x00
    if font == "blit32":
      flags |= 0x01

    self.i2c.writeto_mem(ADDRESS, REG_PATTERN_INDEX, bytes([
      0x03, # 0x37 pattern index
      (offset >> 8) & 0xff, # 0x38 offset high
      offset & 0xff, # 0x39 offset low
      flags, # 0x40 flags
    ]))

    if len(text) >= NUM_LEDS:
      print(f"Warning: text too long {len(text)}, will be truncated after {NUM_LEDS -1}")

  @staticmethod
  def match_header(header: HexpansionHeader):
    return header.friendly_name == "Liteloop"

  @staticmethod
  def name():
    return "Liteloop"

  @staticmethod
  def patterns():
    return [
      (0, "Fill"),
      # (1, "Spirit level"), # TODO pattern using IMU not implemented yet
      (2, "Starfield"),
      # (3, "Text"), # (this is used by the set_text method instead as it needs extra data)
    ]

  @staticmethod
  def matrix():
    return {
      "rows": 9,
      "cols": 18,
      "grid": [
        None, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, None, None, None,
        12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 114, 115, 116, 117, 118, 119,
        24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 126, 127, 128, 129, 130, 131,
        36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 138, 139, 140, 141, 142, 143,
        48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 150, 151, 152, 153, 154, 155,
        60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 108, 109, 110, 111, 112, 113,
        72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 120, 121, 122, 123, 124, 125,
        84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 132, 133, 134, 135, 136, 137,
        96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 144, 145, 146, 147, 148, 149,
      ]
    }