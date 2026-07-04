import math

from app_components import Menu, tokens
import re

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

# Menu names, may be displayed but must also be unique
MENU_MAIN = "Main"
MENU_FIRMWARE_UPDATE = "Firmware Update"
MENU_HELP = "Help"
MENU_PATTERN_PORT = "Pattern port"
MENU_PATTERN_PATTERN = "Pattern"
MENU_ALL_OFF = "All off"
MENU_ALL_DEFAULT = "All default"
MENU_TEXT = "Text"

# Menu item names, only for display, don't have to be unique
ALL_OFF = "All off"
ALL_DEFAULT = "All to default"
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

      # TODO workaround to clear port highlighting on return to main menu
      if menu_name == MENU_MAIN:
        self.menu_state["selected_boards"] = []

  def change(self, item):
    # TODO explicitly set these
    if re.match("^P\d:", item):
      self.highlighted_ports=[int(item[1])]
    else:
      self.highlighted_ports=[]

  def update(self, delta):
    self.menu.update(delta)

  def draw(self, ctx):
    draw_ports(ctx, self.highlighted_ports, [b.port for b in self.menu_state.get("selected_boards", [])])
    self.menu.draw(ctx)

  def get_menu_items(self, menu_name):
    if menu_name == MENU_MAIN:
      return [
        (ALL_OFF, lambda: self.set_menu(MENU_ALL_OFF)),
        (ALL_DEFAULT, lambda: self.set_menu(MENU_ALL_DEFAULT)),
        (TEXT, lambda: self.set_menu(MENU_TEXT)),
        (PATTERN, lambda: self.set_menu(MENU_PATTERN_PORT)),
        (FIRMWARE_UPDATE, lambda: self.set_menu(MENU_FIRMWARE_UPDATE)),
        (HELP, lambda: self.set_menu(MENU_HELP)),
        (SETTINGS, lambda: self.set_menu(SETTINGS)),
      ]
    elif menu_name == MENU_PATTERN_PORT:
      self.app.scan_boards()
      filtered_boards = [board for board in self.app.boards if len(board.patterns()) > 0]

      if len(filtered_boards) == 0:
        return [(NOT_FOUND, None)]

      groups = []
      for board in filtered_boards:
        found = False
        for boards in groups:
          if board.name() == boards[0].name():
            boards.append(board)
        if not found:
          groups.append([board])
      
      return [
        (
          f"All '{boards[0].name()}' (x{len(boards)})", 
        ) for boards in groups if len(boards) > 1
      ] + [
        (
          f"P{board.port}: {board.name()}",
          lambda board=board: self.set_menu(MENU_PATTERN_PATTERN, selected_boards=[board]),
        ) for board in filtered_boards
      ]
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
    else:
      return [
        (NOT_IMPLEMENTED, None),
        (f"({menu_name})", None),
      ]



def draw_ports(ctx, highlighted, selected):
  for port in range(1, 7):
    color = None
    if port in highlighted:
      color = "orange"
    if port in selected:
      color = "yellow"

    if color is None:
      continue
    
    ctx.save()
    ctx.rotate(math.pi / 180 * ((port - 2) * 60))
    tokens.set_color(ctx, color)
    ctx.move_to(100, 0)
    ctx.text(tokens.symbols["pointing_triangles"]["right"])
    ctx.restore()