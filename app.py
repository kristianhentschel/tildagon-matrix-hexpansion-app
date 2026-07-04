import app
from machine import I2C
from events.input import Buttons, BUTTON_TYPES
from system.eventbus import eventbus
from system.hexpansion.events import HexpansionMountedEvent, HexpansionUnmountedEvent
from system.hexpansion.util import read_hexpansion_header
from system.hexpansion.config import HexpansionConfig
from app_components import clear_background

from .menu import MatrixHexpansionMenu
from .events import MatrixHexpansionToast
from .firmware import MatrixHexpansionFirmware
from .liteloop import LiteLoop

VID = 0xCAFE
PID = 0x54E1
EEPROM_ADDRESS = 0x50

BOARDS = [
  LiteLoop,
]

class MatrixHexpansionApp(app.App):
  def __init__(self):
    self.boards = []
    self.scan_boards()

    eventbus.on(MatrixHexpansionToast, self.handle_toast, self)

    # TODO check if mounted or inserted event is needed for hexpansions with header-only eeprom
    eventbus.on(HexpansionMountedEvent, self.scan_boards, self)
    eventbus.on(HexpansionUnmountedEvent, self.scan_boards, self)
    # eventbus.on(HexpansionInsertionEvent, self.scan_boards, self)
    # eventbus.on(HexpansionRemovalEvent, self.scan_boards, self)

    self.menu = MatrixHexpansionMenu(self)

  def update(self, delta):
    self.menu.update(delta)

  def draw(self, ctx):
    clear_background(ctx)
    self.menu.draw(ctx)

  def handle_toast(self, event):
    if isinstance(event, MatrixHexpansionToast):
      print(f"Got toast {event.text}")
    else:
      print(f"Got some other event {event}")

  def scan_boards(self):
    results = []
    for port in range(1, 7):
      i2c = I2C(port)
      header = read_hexpansion_header(i2c, eeprom_addr=EEPROM_ADDRESS)
      if header:
        print(port, VID, header.vid, PID, header.pid, header.friendly_name)
        for board in BOARDS:
          if header.vid == VID and header.pid == PID and board.match_header(header):
            results.append(board(HexpansionConfig(port), header))
            break
    print(f"Found {len(self.boards)} matching hexpansions")
    self.boards = results

__app_export__ = MatrixHexpansionApp