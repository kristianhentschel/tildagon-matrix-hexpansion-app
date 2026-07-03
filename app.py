import app
from machine import I2C
from events.input import Buttons, BUTTON_TYPES
from system.eventbus import eventbus
from system.hexpansion.events import HexpansionMountedEvent, HexpansionUnmountedEvent
from system.hexpansion.util import get_slots_by_vid_pid, read_hexpansion_header
from system.hexpansion.config import HexpansionConfig
from app_components import Menu, clear_background

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
        self.button_states = Buttons(self)
        self.boards = []

        self.scan_boards()

        eventbus.on(MatrixHexpansionToast, self.handle_toast, self)

        eventbus.on(HexpansionMountedEvent, self.scan_boards, self)
        eventbus.on(HexpansionUnmountedEvent, self.scan_boards, self)
        # eventbus.on(HexpansionInsertionEvent, self.scan_boards, self)
        # eventbus.on(HexpansionRemovalEvent, self.scan_boards, self)

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays open.
            # Without it the app would close again immediately.
            self.button_states.clear()
            self.minimise()

            # Not removing event handler on minimise so that we can still react to events from other apps
            # eventbus.remove(MatrixHexpansionToast, self.handle_toast, self.app)

        if self.button_states.get(BUTTON_TYPES["CONFIRM"]):
            fw = MatrixHexpansionFirmware(1)
            # fw.flash_firmware("/blink.bin")
            fw.flash_firmware("/apps/kristianhentschel_tildagon_matrix_hexpansion_app/assets/firmware.lite_loop.ch32v006.bin")
            
    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 0, 0).move_to(-80, 0).text("Hello world")
        ctx.restore()

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