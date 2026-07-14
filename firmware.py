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
COLOUR_OFF = [0, 0, 0]

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


  @staticmethod
  def port_is_used(port):
    """ Checks if a hexpansion is detected in the given port """
    nd_pin = ePin(PORT_ND_PINS[port - 1])
    return nd_pin.value() == 0

  @staticmethod
  def set_port_led(port, colour):
    """ Sets the LED associated with that port to a specific colour """
    led = 12 + port
    tildagonos.leds[led] = colour
    tildagonos.leds.write()

  @staticmethod
  def reboot_port(port, bootloader=False):
    """ Cuts power to the hexpansion port briefly and sets the bootloader request pin if needed """
    try:
      config = HexpansionConfig(port)
      power_pin = ePin(PORT_ND_PINS[port - 1])
      bootloader_pin = config.pin[1]

      MatrixHexpansionFirmware.set_port_led(port, COLOUR_BOOTING)
      # turn off power to the hexpansion
      power_pin.init(mode=power_pin.OUT)
      power_pin.on() # active low

      # request to access bootloader mode by pulling that pin low
      if bootloader:
        bootloader_pin.init(mode=bootloader_pin.OUT)
        bootloader_pin.off()

      time.sleep(0.25)
    finally:
      MatrixHexpansionFirmware.set_port_led(port, COLOUR_OFF)

      # turn power back on (if a hexpansion is plugged in it pulls the pin low if it is configured as an input)
      power_pin.init(mode=power_pin.IN)
      time.sleep(0.25)

      # Reset bootloader pin to input (to not interfere with matrix operations)
      bootloader_pin.init(mode=bootloader_pin.IN)


  @staticmethod
  def bootloader_is_present(port):
    """ Checks if the bootloader responds at the expected I2C address """
    config = HexpansionConfig(port)
    return BOOTLOADER_ADDRESS in config.i2c.scan()

  @staticmethod
  def read_bootloader_status(port):
    config = HexpansionConfig(port)
    i2c = config.i2c

    # Read status
    i2c.writeto(BOOTLOADER_ADDRESS, bytes([0x00, 0x00]))
    data = i2c.readfrom(BOOTLOADER_ADDRESS, 8).hex()

    return {
      "bytes": data
      # TODO parse chip id, memory size, last page written from response
    }

  @staticmethod
  def get_num_pages(data):
    return math.ceil(len(data) / 256)

  @staticmethod
  def get_page_data(data, i):
    start = i * 256
    end = start + 256
    if end < len(data):
      return data[start:end]
    if start >= len(data):
      return b"\x00" * 256
    else:
      return data[start:len(data)] + b"\x00" * (end - len(data))

  @staticmethod
  def upload_image(port, image, verify=False, garbage=None):
    config = HexpansionConfig(port)
    i2c = config.i2c

    with open(image, "rb") as f:
      data = f.read()
      print(f"Flashing {round(len(data) / 1024, 1)}K {image} to hexpansion on {port}")

      num_pages = MatrixHexpansionFirmware.get_num_pages(data)

      for i in range(num_pages):
        MatrixHexpansionFirmware.set_port_led(port, COLOUR_WRITING if i % 2 == 1 else COLOUR_WRITING_2)
        print(f"Writing page {i + 1} / {num_pages}")
        
        # Write page address (0x0100-0x01FF) and page contents
        page_data = MatrixHexpansionFirmware.get_page_data(i)
        
        if garbage is not None:
          page_data = bytes([int(garbage)] * 256)

        # print(f"Page {i}: {len(page_data)} bytes: {page_data.hex()}")
        i2c.writeto(BOOTLOADER_ADDRESS, bytes([0x01, i]) + page_data)

        # Read page just written
        if verify:
          i2c.writeto(BOOTLOADER_ADDRESS, bytes([0x02, i]))
          page_read_data = i2c.readfrom(BOOTLOADER_ADDRESS, 256)

          if page_read_data != page_data:
            raise Exception(f"Verification failed at page {i}")

          # for j in range(16):
          #   print(f"page {bytes([i]).hex()} offset {bytes([j * 16]).hex()} Written: {page_data[16*j:16*(j+1)].hex()} Read:    {page_read_data[16*j:16*(j+1)].hex()}")

  def flash_firmware(self, image: str):
    try:
      self.reboot_port(self.port, bootloader=True)

      if not self.bootloader_is_present(self.port):
        raise Exception(f"Bootloader not active on I2C address 0x{bytes([BOOTLOADER_ADDRESS]).hex()}")

      self.set_port_led(self.port, COLOUR_WRITING)

      self.upload_image(self.port, image, verify=True)

      self.set_port_led(self.port, COLOUR_DONE)

      print(f"Firmware upgrade complete")
        
    except Exception as e:
      self.set_port_led(self.port, COLOUR_ERROR)
      return f"Upgrade failed: {e}"
    finally:
      # ensure badge pins are configured as inputs again
      self.reboot_port(self.port, bootloader=False)
