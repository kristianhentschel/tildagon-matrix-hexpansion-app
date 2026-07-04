from app_components import Menu, tokens

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

# Menu names, may be displayed but must also be unique
MENU_MAIN = "Main"
MENU_FIRMWARE_UPDATE = "Firmware Update"
MENU_HELP = "Help"
MENU_PATTERN_PORT = "Pattern port"
MENU_PATTERN_PATTERN = "Pattern"

# Menu item names, only for display, don't have to be unique
ALL_OFF = "All off"
ALL_DEFAULT = "All to default"
TEXT = "Text"
PATTERN = "Pattern"
FIRMWARE_UPDATE = "Firmware update"
HELP = "Help"
SETTINGS = "Settings"

class MatrixHexpansionMenu:
  def __init__(self, app):
    self.app = app
    self.menu = None
    self.menu_items = []
    self.menu_stack = []
    self.menu_name = MENU_MAIN
    self.menu_state = {}

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
    self.menu = Menu(self.app,
                     [label for label, callback in self.menu_items],
                     item_font_size=tokens.small_font_size,
                     focused_item_font_size=tokens.label_font_size,
                     position=position,
                     item_line_height=tokens.line_height*tokens.small_font_size,
                     select_handler=self.select, back_handler=self.back)

  def select(self, item, position):
    name, cb = self.menu_items[position]
    print(f"selected {name} at {position} (callback: {cb})")

    if cb is not None:
      cb()

  def back(self):
    print(f"BACK stack size {len(self.menu_stack)}")
    if len(self.menu_stack) == 0:
      self.app.minimise()
    else:
      menu_name, position = self.menu_stack.pop()
      self.set_menu(menu_name, position=position, back=True)

  def update(self, delta):
    self.menu.update(delta)

  def draw(self, ctx):
    self.menu.draw(ctx)

  def get_menu_items(self, menu_name):
    if menu_name == MENU_MAIN:
      return [
        (ALL_OFF, None),
        (ALL_DEFAULT, None),
        (TEXT, None),
        (PATTERN, lambda: self.set_menu(MENU_PATTERN_PORT)),
        (FIRMWARE_UPDATE, lambda: self.set_menu(MENU_FIRMWARE_UPDATE)),
        (HELP, lambda: self.set_menu(MENU_HELP)),
        (SETTINGS, None),
      ]
    elif menu_name == MENU_PATTERN_PORT:
      filtered_boards = [board for board in self.app.boards if len(board.patterns()) > 0]
      self.app.scan_boards()
      
      return [
        ("All", None),
      ] + [
        (
          f"P{board.port} {board.name()}",
          lambda board=board: self.set_menu(MENU_PATTERN_PATTERN, selected_boards=[board]),
        ) for board in filtered_boards
      ] + [
        ("", None),
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
        return [("N/A", None)]
    else:
      return [
        ("Nothing to see here", None),
        (f"(this is {menu_name})", None),
      ]