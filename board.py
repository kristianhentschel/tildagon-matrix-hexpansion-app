from system.hexpansion.header import HexpansionHeader
from .firmware import MatrixHexpansionFirmware
from machine import I2C
import time

# TODO refactor this is duplicated in firmware.py as that also needs to reboot a hexpansion
from tildagonos import tildagonos, EPIN_ND_A, EPIN_ND_B, EPIN_ND_C, EPIN_ND_D, EPIN_ND_E, EPIN_ND_F
from egpio import ePin

PORT_ND_PINS = [
  EPIN_ND_A,
  EPIN_ND_B,
  EPIN_ND_C,
  EPIN_ND_D,
  EPIN_ND_E,
  EPIN_ND_F,
]

class Board:
  def __init__(self, config: HexpansionConfig, header: HexpansionHeader):
    self.config = config
    self.port = config.port
    self.i2c = I2C(config.port)
    self.header = header

  @staticmethod
  def match_header():
    return True

  @staticmethod
  def name():
    return ""

  def flash_firmware(self, image: str):
    return MatrixHexpansionFirmware(self.port).flash_firmware(image)

  def set_all(self, level: int):
    pass

  def set_on_off_image(self, packed):
    pass

  def set_pwm_image(level):
    pass

  def set_pattern(index: int):
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

  