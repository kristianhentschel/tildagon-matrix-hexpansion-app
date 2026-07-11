from system.hexpansion.config import HexpansionConfig
from system.hexpansion.header import HexpansionHeader
from .firmware import MatrixHexpansionFirmware

class Board:
  def __init__(self, config: HexpansionConfig, header: HexpansionHeader):
    self.config = config
    self.port = config.port
    self.i2c = config.i2c
    self.header = header

  @staticmethod
  def match_header():
    return True

  @staticmethod
  def name():
    return ""

  def flash_firmware(self, image: str):
    return MatrixHexpansionFirmware(self.port).flash_firmware(image)

  def set_fill(level: int):
    pass

  def set_pattern(index: int):
    pass

  def set_image(values: list):
    pass

  @staticmethod
  def matrix():
    return {
      "rows": 0,
      "cols": 0,
      "grid": []
    }

  def __str__(self):
    return f"{self.port}: {self.name()}"

  