from system.hexpansion.config import HexpansionConfig
from system.hexpansion.header import HexpansionHeader
from .board import Board

ADDRESS = 0x20

REG_PATTERN_INDEX = 0x37
REG_DIRECT_CONTROL = 0x50

class LiteLoop (Board):
  def __init__(self, config: HexpansionConfig, header: HexpansionHeader):
    super(config, header)

  def set_pattern(self, pattern_index):
    # select pattern
    self.config.i2c.writeto_mem(ADDRESS, REG_PATTERN_INDEX, bytes([pattern_index]))
    
    # disable direct control
    self.config.i2c.writeto_mem(ADDRESS, REG_DIRECT_CONTROL, bytes([0]))

  @staticmethod
  def match_header(header: HexpansionHeader):
    return header.friendly_name == "Liteloop"

  @staticmethod
  def name():
    return "lite-loop"

  @staticmethod
  def patterns():
    return [
      (0, "Fill"),
      (1, "Count scroll"),
      (2, "Starfield"),
    ]