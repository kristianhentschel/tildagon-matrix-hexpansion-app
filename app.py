import app
import asyncio
import time
from machine import I2C
from events.input import Buttons, BUTTON_TYPES
from system.eventbus import eventbus
# from system.hexpansion.events import HexpansionMountedEvent, HexpansionUnmountedEvent
from system.hexpansion.events import HexpansionInsertionEvent, HexpansionRemovalEvent
from system.hexpansion.util import read_hexpansion_header
from system.hexpansion.config import HexpansionConfig
from app_components import clear_background

from .menu import MatrixHexpansionMenu
from .events import MatrixHexpansionToast
from .firmware import MatrixHexpansionFirmware
from .board_liteloop import LiteLoopBoard
from .board_unknown import UnknownBoard
from .board_unresponsive import UnresponsiveBoard

VID = 0xCAFE
PID = 0x54E1
EEPROM_ADDRESS = 0x50

BOARDS = [
  LiteLoopBoard,
  UnknownBoard,
]

class MatrixHexpansionApp(app.App):
  def __init__(self):
    self.boards = []
    # self.scan_boards() # scan on relevant menus, for faster startup

    eventbus.on(MatrixHexpansionToast, self.handle_toast, self)

    # TODO check if mounted or inserted event is needed for hexpansions with header-only eeprom
    # eventbus.on(HexpansionMountedEvent, self.scan_boards, self)
    # eventbus.on(HexpansionUnmountedEvent, self.scan_boards, self)
    eventbus.on(HexpansionInsertionEvent, self.scan_boards, self)
    eventbus.on(HexpansionRemovalEvent, self.scan_boards, self)

    self.menu = MatrixHexpansionMenu(self)

    self.scrolling_text = None
    self.scrolling_text_offset = None

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
      try:
        header = read_hexpansion_header(i2c, eeprom_addr=EEPROM_ADDRESS)
      except Exception as e:
        print(e)
        header = None
      if header:
        # print(port, VID, header.vid, PID, header.pid, header.friendly_name)
        if header.vid == VID and header.pid == PID:
          # one of ours, find out which one:
          for board in BOARDS:
            if board.match_header(header):
              results.append(board(HexpansionConfig(port), header))
              break
        else:
          # unknown board with a header though, get friendly name
          results.append(UnknownBoard(HexpansionConfig(port), header))
      elif MatrixHexpansionFirmware.port_is_used(port):
        # no header, but perhaps one that could be flashed
        results.append(UnresponsiveBoard(HexpansionConfig(port), None))
      else:
        # nothing plugged in
        pass

    self.boards = results
    # print(f"Found {len(self.boards)} hexpansions connected {[str(board) for board in results]}")

  def display_text(self, text, scroll_offset = None):
    # TODO refactor and separate set_scrolling_text from update_/advance_
    self.scrolling_text = text
    self.scrolling_text_offset = scroll_offset

    if scroll_offset is not None:
      self.scrolling_text_offset = scroll_offset
    else:
      self.scrolling_text_offset = None

    if self.scrolling_text_offset is not None:
      dx = self.scrolling_text_offset # TODO don't have a negative offset so may need to calculate offsets individually
    else:
      dx = 18 # on first board it should be offset to fully display as it is not scrolling text yet
    
    for board in reversed([board for board in self.boards if isinstance(board, LiteLoopBoard)]):
      try: 
        board.set_text(text, font="blit16", offset=dx)
        dx += board.matrix()["cols"]
      except Exception as e:
        print(f"Failed to render text on {board.port}: {e}")
        break
  
  def clear_scrolling_text(self):
    self.scroll_offset = None
    self.scrolling_text = None

  def background_update(self, delta):
    # TODO use delta for constant scrolling rate
      if self.scrolling_text is not None and self.scrolling_text_offset is not None:
        self.display_text(self.scrolling_text, scroll_offset=(self.scrolling_text_offset + 1) % max(6 * 16, len(self.scrolling_text) * 4))

__app_export__ = MatrixHexpansionApp