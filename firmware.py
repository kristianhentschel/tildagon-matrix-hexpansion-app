from tildagonos import tildagonos, EPIN_ND_A, EPIN_ND_B, EPIN_ND_C, EPIN_ND_D, EPIN_ND_E, EPIN_ND_F
from egpio import ePin
import math
import time
from system.hexpansion.config import HexpansionConfig

BOOTLOADER_ADDRESS = 0x2A

COLOUR_BOOTING = [255, 255, 255]
COLOUR_WRITING = [32, 32, 255]
COLOUR_WRITING_2 = [32, 32, 32]
COLOUR_ERROR = [127, 32, 0]
COLOUR_DONE = [0, 127, 32]

PORT_ND_PINS = [
  EPIN_ND_A,
  EPIN_ND_B,
  EPIN_ND_C,
  EPIN_ND_D,
  EPIN_ND_E,
  EPIN_ND_F,
]

class MatrixHexpansionFirmware:
  def __init__(self, port):
    self.config = HexpansionConfig(port)
    self.port = self.config.port
    self.i2c = self.config.i2c

    self.led = 12 + self.port
    self.nd_pin = ePin(PORT_ND_PINS[self.port - 1])

  def set_led_colour(self, colour):
    tildagonos.leds[self.led] = colour
    tildagonos.leds.write()

  def flash_firmware(self, image: str):
    bootloader_pin = self.config.pin[1]
    power_pin = self.nd_pin

    try:
      # Power cycle board and hold PD7 (HS_G) low during boot to enter bootloader
      power_pin.init(mode=bootloader_pin.OUT)
      power_pin.on() # active low
      self.set_led_colour(COLOUR_BOOTING)
      time.sleep(0.25)

      bootloader_pin.init(mode=bootloader_pin.OUT)
      bootloader_pin.off()

      power_pin.init(mode=power_pin.IN) # will be pulled low again if hexpansion is inserted
      time.sleep(0.25)

      scan_result = self.i2c.scan()
      if not BOOTLOADER_ADDRESS in scan_result:
        raise Exception(f"Bootloader not active on I2C address 0x{bytes([BOOTLOADER_ADDRESS]).hex()}")

      self.set_led_colour(COLOUR_WRITING)
      # Read the firmware image from the file system and flash it
      with open(image, "rb") as f:
        data = f.read()
        print(f"Flashing {round(len(data) / 1024, 1)}K {image} to hexpansion on {self.port}")

        def page(n):
          start = n * 256
          end = start + 256
          if end < len(data):
            return data[start:end]
          if start >= len(data):
            return b"\x00" * 256
          else:
            return data[start:len(data)] + b"\x00" * (end - len(data))
            
        num_pages = math.ceil(len(data) / 256)

        # Write status register address; read status register
        self.i2c.writeto(BOOTLOADER_ADDRESS, bytes([0x00, 0x00]))
        print(f"Bootloader status registers: {self.i2c.readfrom(BOOTLOADER_ADDRESS, 8).hex()}")

        # TODO verify flash size and MCU model matches image, perhaps by filename convention

        for i in range(num_pages):
          self.set_led_colour(COLOUR_WRITING if i % 2 == 1 else COLOUR_WRITING_2)

          print(f"writing page {i + 1} / {num_pages}")
          
          # Write page address (0x0100-0x01FF) and page contents
          self.i2c.writeto(BOOTLOADER_ADDRESS, bytes([0x01, i]) + page(i))

        # TODO verify programmed image
        self.set_led_colour(COLOUR_DONE)
        print(f"Firmware upgrade complete")
        
      # TODO need to do anything to reboot into user code now, or power cycle again?
    except Exception as e:
      self.set_led_colour(COLOUR_ERROR)
      print(f"Failed to flash image: {e}")
      # TODO return error state to menu or at least raise a toast
    finally:
      # ensure badge pins are configured as inputs again
      power_pin.init(mode=self.nd_pin.IN)
      bootloader_pin.init(mode=bootloader_pin.IN)
