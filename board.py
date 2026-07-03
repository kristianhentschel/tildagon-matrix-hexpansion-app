from system.hexpansion.config import HexpansionConfig
from system.hexpansion.header import HexpansionHeader

class Board:
  def __init__(self, config: HexpansionConfig, header: HexpansionHeader):
    self.config = config
    self.port = config.port
    self.i2c = config.i2c

    self.header = header

  @staticmethod
  def match_header():
    return True

  def flash_firmware(self, image: str):
    MatrixHexpansionFirmware.flash_firmware