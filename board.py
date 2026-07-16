from system.hexpansion.config import HexpansionConfig
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

class BadI2C (I2C):
  """ This wraps the native I2C class and reboots the hexpansion on writeto errors; this should
  resolve lock ups from I2C clock extensions if something somewhere is hanging. """
  def __init__(self, port):
    super().__init__(port)
    self.port = port

  def reboot(self):
    power_pin = ePin(PORT_ND_PINS[self.port - 1])
    
    # briefly cut power to hexpansion port
    power_pin.init(mode=power_pin.OUT)
    power_pin.on()
    time.sleep(0.5)

    # reset power pin to input, re-enables power
    power_pin.init(mode=power_pin.IN)

    print("wakey wakey")

  def writeto(self, *args, **kwargs):
    try:
      return super().writeto(*args, *kwargs)
    except Exception as err:
      print(f"{err}, cutting power...")
      self.reboot()

      return 0

  def writeto_mem(self, *args, **kwargs):
    try:
      return super().writeto_mem(*args, *kwargs)
    except Exception as err:
      print(f"{err}, cutting power...")
      self.reboot()

      return 0

class Board:
  def __init__(self, config: HexpansionConfig, header: HexpansionHeader):
    self.config = config
    self.port = config.port
    self.i2c = BadI2C(config.port)
    self.header = header

  @staticmethod
  def match_header():
    return True

  @staticmethod
  def name():
    return ""

  def flash_firmware(self, image: str):
    return MatrixHexpansionFirmware(self.port).flash_firmware(image)

  def set_all(level: int):
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

  