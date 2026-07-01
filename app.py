import app

from events.input import Buttons, BUTTON_TYPES
from system.eventbus import eventbus
from .events import MatrixHexpansionToast

class MatrixHexpansionApp(app.App):
    def __init__(self):
        self.button_states = Buttons(self)

        eventbus.on(MatrixHexpansionToast, self.handle_toast, self)

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
            eventbus.emit(MatrixHexpansionToast("Self-centred event"))
            
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

__app_export__ = MatrixHexpansionApp