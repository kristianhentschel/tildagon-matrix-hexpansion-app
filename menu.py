import math
import re
import os
from app_components import Menu, Notification, tokens
import time
from .text import TextDisplay

# MAIN
#  ALL OFF
#  ALL DEFAULT
#  TEXT
#   ENTER TEXT
#   SELECT TEXT
#     TEXTS
#       SCROLL ONCE
#       DISPLAY STATIC
#       COPY
#         EDIT TEXT
#       REMOVE
#  PATTERN
#    ALL [BOARD]
#      PATTERN
#    PORT x [BOARD]
#      PATTERN
#  FIRMWARE UPDATE
#   IMAGE
#    SLOT
#     CONFIRM
#  HELP
#  SETTINGS
#   Clear default assignments
#   Clear saved texts
#   Accept text from other apps
#   Accept images from other apps
#   React to emote events

ASSET_PATH="/apps/kristianhentschel_tildagon_matrix_hexpansion_app/assets/"

# Menu names, may be displayed but must also be unique
MENU_MAIN = "Main"
MENU_FIRMWARE_UPDATE_PORT = "Firmware update port"
MENU_FIRMWARE_UPDATE_IMAGE = "Firmware update image"
MENU_HELP = "Help"
MENU_PATTERN_PORT = "Pattern port"
MENU_PATTERN_PATTERN = "Pattern"
MENU_TEXT = "Text"
MENU_STATIC = "Static"

# Menu item names, only for display, don't have to be unique
ALL_DEFAULT = "All to default"
ALL_STATIC = "All static"
TEXT = "Text"
PATTERN = "Pattern"
FIRMWARE_UPDATE = "Firmware update"
HELP = "Help"
SETTINGS = "Settings"
ALL = "All"
NOT_FOUND = "N/A"
NOT_IMPLEMENTED = "Not implemented"

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

    self.set_menu(self.menu_name)
  
  def set_menu(self, menu_name, position=0, back=False, **state):
    # Clean up previous menu and save its name to return to on BACK
    if self.menu is not None:
      if not back:
        self.menu_stack.append((self.menu_name, self.menu.position))
      self.menu._cleanup()

    # Update state variables before entering the next menu
    for key in state:
      self.menu_state[key] = state[key]
    
    # Generate menu items for the new menu and instantiate it
    self.menu_items = self.get_menu_items(menu_name)
    self.menu_name = menu_name
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
    name, cb = self.menu_items[position]

    if cb is not None:
      cb()

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
    self.menu.update(delta)
    if (self.notification):
      self.notification.update(delta)

  def draw(self, ctx):
    draw_ports(ctx, self.highlighted_ports, [b.port for b in self.menu_state.get("selected_boards", [])])
    self.menu.draw(ctx)
    if (self.notification):
      self.notification.draw(ctx)

  def get_menu_items(self, menu_name):
    if menu_name == MENU_MAIN:
      def all_default():
        self.app.scan_boards()
        print(f"Setting default pattern on {len(self.app.boards)} boards")
        for board in self.app.boards:
          try:
            board.set_default_pattern()
          except Exception as e:
            print("error setting default pattern", e)
        time.sleep(0.05)
        self.notification = Notification(ALL_DEFAULT)

      return [
        (ALL_STATIC, lambda: self.set_menu(MENU_STATIC)),
        (ALL_DEFAULT, lambda: all_default()),
        (TEXT, lambda: self.set_menu(MENU_TEXT)),
        (PATTERN, lambda: self.set_menu(MENU_PATTERN_PORT)),
        (FIRMWARE_UPDATE, lambda: self.set_menu(MENU_FIRMWARE_UPDATE_PORT)),
        (HELP, lambda: self.set_menu(MENU_HELP)),
        (SETTINGS, lambda: self.set_menu(SETTINGS)),
      ]
    elif menu_name == MENU_PATTERN_PORT:
      return self.get_boards_menu_items(MENU_PATTERN_PATTERN, include_groups=True, pattern_only=True)
    elif menu_name == MENU_PATTERN_PATTERN:
      try:
        boards = self.menu_state["selected_boards"]
        board = boards[0]

        def set_pattern(code):
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
        self.app.scan_boards()
        for board in self.app.boards:
          try:
            board.set_fill(level)
          except Exception as e:
            print("error setting static fill", e)
        time.sleep(0.05)
        self.notification = Notification(ALL_STATIC + f" {level}")

      return [(f"{level}", lambda level=level: all_static(level)) for level in [0, 1, 31, 63, 127, 255]]
    elif menu_name == MENU_FIRMWARE_UPDATE_PORT:
      return self.get_boards_menu_items(MENU_FIRMWARE_UPDATE_IMAGE, include_unknown=True, include_unresponsive=True)
    elif menu_name == MENU_FIRMWARE_UPDATE_IMAGE:
      # TODO list assets/firmware updates folder
      board = self.menu_state["selected_boards"][0]
      images = [
        (name, ASSET_PATH + name) for name in os.listdir(ASSET_PATH) if name.endswith(".bin")
      ]

      if len(images) == 0:
        return [
          NOT_FOUND, None
        ]

      def flash_firmware(image_path):
        err = board.flash_firmware(image_path)
        if (err):
          self.notification = Notification(err)
        else:
          self.notification = Notification("Firmware updated")

        # TODO workaround - return back to port selection
        # TODO this immediately scans hexpansions and if it's still in bootloader mode it will show as unresponsive (modify bootloader to take an immediate reboot command)
        self.back()

      # TODO firmware upgrade progress, error handling
      return [
        (image_name, lambda image_path=image_path: flash_firmware(image_path)) for image_name, image_path in images
      ]
    elif menu_name == MENU_TEXT:
      def display_text(text):
        self.app.scan_boards()
        dx = 18 # on first board it should be offset to fully display as it is not scrolling text yet
        for board in reversed(self.app.boards): # reversed to go in left to right order with baseline outwards
          print(f"{text} for port {board.port}")
          try: 
            board.set_text(text, font="blit16", offset=dx)
            dx += board.matrix()["cols"]
          except Exception as e:
            print(f"Failed to render text on {board.port}: {e}")
            break
          # try:
          #   t = TextDisplay(board)
          #   t.render(text, offset=dx, font="blit32" if len(text) < 8 else "blit16")
          #   t.display()
          #   time.sleep(0.05)
          #   dx += board.matrix()["cols"] # TODO expose grid width without having to get the full matrix()
          # except Exception as e:
          #   print(f"Failed to render text on {board.port}: {e}")

      lines = [
        "EMF",
        "#EMFCamp",
        "Chillin'",
        "LEDbury",
        "#badgelife",
        "HACK THE PLANET",
        "You know the rules, and so do I",
        "You too can be a walking billboard... buy a matrix hexpansion today!",
        "This is the void chat, crossing the spectrum.\nThe field is against her but she's on time.\nLetters for the rich, letters for the poor,\nthe dome at the corner, and the ducks next door.\nHalf a million spiders are sorted, picked up, or dropped during the night.",
        "Help I'm stuck in a hexpansion assembly line",
      ]

      return [
        (line if len(line) < 20 else line[0:18] + "...", lambda line=line: display_text(line)) for line in lines
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