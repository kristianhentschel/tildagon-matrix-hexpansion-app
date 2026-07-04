from system.hexpansion.config import HexpansionConfig
from system.hexpansion.header import HexpansionHeader
from .board import Board

ADDRESS = 0x20

REG_PATTERN_INDEX = 0x37
REG_DIRECT_CONTROL = 0x50

class UnknownBoard (Board):
  def __init__(self, config: HexpansionConfig, header: HexpansionHeader):
    # TODO: may not have a header at all, would we still use this this calss
    super().__init__(config, header)

  def set_pattern(self, pattern_index):
    pass

  @staticmethod
  def match_header(header: HexpansionHeader):
    return True

  @staticmethod
  def name():
    return "unknown"

  @staticmethod
  def patterns():
    return []