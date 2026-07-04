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
  
  def set_menu(self, menu_name, position=0, back=False):
    if self.menu is not None:
      # save previous menu name for back stack and clean up
      if not back:
        self.menu_stack.append((self.menu_name, self.menu.position))
      self.menu._cleanup()
    
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
        (PATTERN, None),
        (FIRMWARE_UPDATE, lambda: self.set_menu(MENU_FIRMWARE_UPDATE)),
        (HELP, lambda: self.set_menu(MENU_HELP)),
        (SETTINGS, None),
      ]
    else:
      return [
        ("Nothing to see here", None),
        (f"(this is {menu_name})", None),
      ]