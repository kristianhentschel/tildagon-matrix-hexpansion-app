import math
import re
import os
from app_components import Menu, Notification, TextDialog, tokens
import time

ASSET_PATH="/".join(__file__.split("/")[:-1]) + "/assets/"
print(f"ASSET_PATH={ASSET_PATH}")

# Menu names, may be displayed but must also be unique
MENU_MAIN = "Main"
MENU_FIRMWARE_UPDATE_PORT = "Firmware update port"
MENU_FIRMWARE_UPDATE_IMAGE = "Firmware update image"
MENU_HELP = "Help"
MENU_PATTERN_PORT = "Pattern port"
MENU_PATTERN_PATTERN = "Pattern"
MENU_TEXT = "Text"
MENU_STATIC = "Static"
MENU_TEXT_ENTRY = "Text entry"

# Menu item names, only for display, don't have to be unique
ALL_DEFAULT = "All to default"
ALL_STATIC = "All to constant"
TEXT = "Text"
PATTERN = "Pattern"
FIRMWARE_UPDATE = "Firmware update"
HELP = "Help"
SETTINGS = "Settings"
ALL = "All"
NOT_FOUND = "N/A"
NOT_IMPLEMENTED = "Not implemented"
CHECK_FIRMWARE_UPDATE = "Fetch latest..."

FIRMWARE_VERSION="v0.0.2"
FIRMWARE_DOWNLOAD_URL=f"https://github.com/kristianhentschel/tildagon-matrix-hexpansion/releases/download/{FIRMWARE_VERSION}/lite_loop.bin"

class MatrixHexpansionMenu:
  def __init__(self, app):
    self.app = app
    self.menu = None
    self.menu_items = []
    self.menu_stack = []
    self.menu_name = MENU_MAIN
    self.menu_state = {}
    self.highlighted_ports = []
    self.notification = None
    self.dialog = None

    self.set_menu(self.menu_name)

  def list_firmware_images(self):
    firmware_images = []
    try:
      firmware_images = [
        (name, ASSET_PATH + name) for name in os.listdir(ASSET_PATH) if name.endswith(".bin")
      ]
    except Exception as e:
      print(f"could not list firmware images: {e}")

    return firmware_images
  
  def set_menu(self, menu_name, position=0, back=False, **state):
    # Clean up previous menu and save its name to return to on BACK
    if self.menu is not None:
      print(f"menu cleanup {self.menu_name}, back={back}")
      if not back:
        self.menu_stack.append((self.menu_name, self.menu.position))
      self.menu._cleanup()
      self.menu = None
      self.menu_name = None

    # Update state variables before entering the next menu
    for key in state:
      self.menu_state[key] = state[key]
    
    # Generate menu items for the new menu and instantiate it
    self.menu_items = self.get_menu_items(menu_name)
    self.menu_name = menu_name

    if len(self.menu_items) == 0:
      return

    if len(self.menu_items) == 0 or position > len(self.menu_items):
      position = 0
    self.menu = Menu(self.app,
                     [label for label, callback in self.menu_items],
                     item_font_size=tokens.small_font_size,
                     focused_item_font_size=tokens.label_font_size,
                     position=position,
                     item_line_height=tokens.line_height*tokens.small_font_size,
                     select_handler=self.select, back_handler=self.back, change_handler=self.change)
    
    try:
      self.change(self.menu_items[position][0])
    except IndexError:
      pass

  def select(self, item, position):
    try:
      name, cb = self.menu_items[position]

      if cb is not None:
        cb()
    except IndexError:
      pass

  def back(self):
    if len(self.menu_stack) == 0:
      self.app.minimise()
    else:
      menu_name, position = self.menu_stack.pop()
      self.set_menu(menu_name, position=position, back=True)

      # TODO workaround to clear port highlighting on return to some menus
      if menu_name in [MENU_MAIN, MENU_FIRMWARE_UPDATE_PORT, MENU_PATTERN_PORT]:
        self.menu_state["selected_boards"] = []

  def change(self, item):
    # TODO explicitly set these
    if re.match("^P\d:", item):
      self.highlighted_ports=[int(item[1])]
    else:
      self.highlighted_ports=[]

  def update(self, delta):
    if self.dialog is None and self.menu is not None:
        self.menu.update(delta)

    if (self.notification):
      self.notification.update(delta)

  def draw(self, ctx):
    if self.dialog:
      self.dialog.draw(ctx)
    elif self.menu:
      draw_ports(ctx, self.highlighted_ports, [b.port for b in self.menu_state.get("selected_boards", [])])
      self.menu.draw(ctx)
    else:
      # TODO may briefly end up without a menu after text entry, this really shouldn't be in draw but avoids double button handling...
      self.back()

    if self.notification:
      self.notification.draw(ctx)

  def get_menu_items(self, menu_name):
    if menu_name == MENU_MAIN:
      def all_default():
        self.app.clear_scrolling_text()
        self.app.scan_boards()
        print(f"Setting default pattern on {len(self.app.boards)} boards")
        for board in self.app.boards:
          try:
            board.set_default_pattern()
          except Exception as e:
            print("error setting default pattern", e)
        time.sleep(0.05)
        self.notification = Notification(ALL_DEFAULT)

      have_firmware = len(self.list_firmware_images()) > 0

      return [
        (ALL_STATIC, lambda: self.set_menu(MENU_STATIC)),
        (ALL_DEFAULT, lambda: all_default()),
        (TEXT, lambda: self.set_menu(MENU_TEXT)),
        (PATTERN, lambda: self.set_menu(MENU_PATTERN_PORT)),
        (HELP, lambda: self.set_menu(MENU_HELP)),
        (SETTINGS, lambda: self.set_menu(SETTINGS)),
      ] + [(FIRMWARE_UPDATE, lambda: self.set_menu(MENU_FIRMWARE_UPDATE_PORT))] if have_firmware else []
    elif menu_name == MENU_PATTERN_PORT:
      return self.get_boards_menu_items(MENU_PATTERN_PATTERN, include_groups=True, pattern_only=True)
    elif menu_name == MENU_PATTERN_PATTERN:
      try:
        boards = self.menu_state["selected_boards"]
        board = boards[0]

        def set_pattern(code):
          self.app.clear_scrolling_text()
          for b in boards:
            print(f"Setting pattern {code} on board {b}")
            b.set_pattern(code)

        # assume all boards are of the same type
        return [
          (f"{name}", lambda code=code: set_pattern(code))
            for code, name in board.patterns()
        ]
      except Exception as e:
        print(e)
        return [(NOT_FOUND, None)]
    elif menu_name == MENU_STATIC:
      def all_static(level):
        self.app.clear_scrolling_text()
        self.app.scan_boards()
        for board in self.app.boards:
          try:
            board.set_all(level)
          except Exception as e:
            print("error setting static fill", e)
        time.sleep(0.05)
        self.notification = Notification(ALL_STATIC + f" {level}")

      return [(f"{label}", lambda level=level: all_static(level)) for label, level in [
        ("0 (off)", 0),
        (1, 1),
        (2, 2),
        (4, 4),
        (8, 8),
        (16, 16),
        (32, 32),
        (64, 64),
        (128, 128),
        ("255 (100%)", 255),
      ]]
    elif menu_name == MENU_FIRMWARE_UPDATE_PORT:
      return self.get_boards_menu_items(MENU_FIRMWARE_UPDATE_IMAGE, include_unknown=True, include_unresponsive=True, include_groups=True)
    elif menu_name == MENU_FIRMWARE_UPDATE_IMAGE:
      boards = self.menu_state["selected_boards"]
      images = self.list_firmware_images()

      def check_firmware_update():
        print("Firmware update check...")

        self.notification = Notification("Checking...")

        try:
          import requests
          response = requests.get(FIRMWARE_DOWNLOAD_URL)
          filename = f"lite_loop.{FIRMWARE_VERSION}.bin"
          os.makedirs(ASSET_PATH, exist_ok=True)
          with open(ASSET_PATH + filename) as f:
            f.write(response.content)
          self.notification = Notification(f"Downloaded firmware {filename}")
          # TODO not deleting previous versions but maybe we should?
        except Exception as e:
          print(e)
          self.notification = Notification("Failed to fetch updated firmware")
        finally:
          self.set_menu(MENU_FIRMWARE_UPDATE_IMAGE, position=0, back=True)

      if len(images) == 0:
        return [
          (CHECK_FIRMWARE_UPDATE, check_firmware_update),
        ]

      def flash_firmware(image_path):
        for board in boards:
          err = board.flash_firmware(image_path)
          if (err):
            self.notification = Notification(err, port=board.port)
          else:
            self.notification = Notification("Firmware updated", port=board.port)

          # TODO workaround - return back to port selection
          # TODO this immediately scans hexpansions and if it's still in bootloader mode it will show as unresponsive (modify bootloader to take an immediate reboot command)
          self.back()

      # TODO firmware upgrade progress, error handling
      return [
        (image_name, lambda image_path=image_path: flash_firmware(image_path)) for image_name, image_path in images
      ] + [
        (CHECK_FIRMWARE_UPDATE, check_firmware_update)
      ]
    elif menu_name == MENU_TEXT:
      lines = [
        "EMF",
        "#EMFCamp",
        "Chillin'",
        "LEDbury",
        "#badgelife",
        "HACK THE PLANET",
        "You know the rules, and so do I",
        "Help I'm stuck in a hexpansion assembly line",
      ]

      return [
        ("Enter text", lambda: self.set_menu(MENU_TEXT_ENTRY))
      ] + [
        (line if len(line) < 20 else line[0:18] + "...", lambda line=line: self.display_text(line)) for line in lines
      ]
    elif menu_name == MENU_TEXT_ENTRY:
      def complete_handler(text):
        print(f"Complete: text entered was '{text}'")
        self.display_text(text)

      self.start_text_entry("Custom text", complete_handler=complete_handler)
      return []
    elif menu_name == MENU_HELP:
      return [
        # TODO build a proper help screen layout, abusing existing menu system for now
        ("5yk.de/matrix-hexpansion", None)
      ]
    elif menu_name == SETTINGS:
      # TODO implement settings
      return [
        ("Settings", None),
        ("Not yet implemented", None),
      ]
    else:
      return [
        (NOT_IMPLEMENTED, None),
        (f"({menu_name})", None),
      ]

  def get_boards_menu_items(self, next_menu, pattern_only=False, include_groups=False, include_unknown=False, include_unresponsive=False, no_scan=False):
    if not no_scan:
      self.app.scan_boards()

    filtered_boards = self.app.boards
    if pattern_only:
      # this implicitly also filters out unresponsive and unknown because they have no patterns
      filtered_boards = [board for board in filtered_boards if len(board.patterns()) > 0]

    if len(filtered_boards) == 0:
      return [(NOT_FOUND, None)]

    groups = []
    
    if include_groups:
      for board in filtered_boards:
        found = False
        for boards in groups:
          if board.name() == boards[0].name():
            boards.append(board)
            found = True
            break
        if not found:
          groups.append([board])
    
    return [
      (
        f"All '{boards[0].name()}' (x{len(boards)})", 
        lambda boards=boards: self.set_menu(next_menu, selected_boards=boards),
      ) for boards in groups if len(boards) > 1
    ] + [
      (
        f"P{board.port}: {board.name()}",
        lambda board=board: self.set_menu(next_menu, selected_boards=[board]),
      ) for board in filtered_boards
    ]

  def start_text_entry(self, label, complete_handler):
    print("start text entry")
    if self.dialog is not None:
      self.dialog._cleanup()

    def on_complete():
      print("complete: dialog cleanup")
      text = self.dialog.text
      self.dialog._cleanup()
      self.dialog = None
      complete_handler(text)

    def on_cancel():
      print("cancel: dialog cleanup")
      self.dialog._cleanup()
      self.dialog = None

    self.dialog = TextDialog(label, self.app, masked=False, on_complete=on_complete, on_cancel=on_cancel)

  def display_text(self, text):
    self.app.scan_boards()
    self.app.display_text(text, scroll_offset = 0 if len(text) > 9 else None) # TODO depends on number of boards available

def draw_ports(ctx, highlighted, selected):
  for port in range(1, 7):
    color = None
    if port in highlighted:
      color = "orange"
    elif port in selected:
      color = "yellow"

    if color is None:
      continue
    
    ctx.save()
    ctx.rotate(math.pi / 180 * ((port - 2) * 60))
    tokens.set_color(ctx, color)
    ctx.font_size = 16
    ctx.text_baseline = ctx.MIDDLE
    ctx.text_align = ctx.RIGHT
    ctx.move_to(120, 0)
    ctx.text(tokens.symbols["pointing_triangles"]["right"])
    ctx.restore()