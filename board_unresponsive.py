from system.hexpansion.config import HexpansionConfig
from system.hexpansion.header import HexpansionHeader
from .board import Board

ADDRESS = 0x20

REG_PATTERN_INDEX = 0x37
REG_DIRECT_CONTROL = 0x50

class UnresponsiveBoard (Board):
  def __init__(self, config: HexpansionConfig, header: HexpansionHeader):
    super().__init__(config, None)

  def set_pattern(self, pattern_index):
    pass

  @staticmethod
  def match_header(header: HexpansionHeader):
    return False

  @staticmethod
  def name():
    return "unresponsive"

  @staticmethod
  def patterns():
    return []