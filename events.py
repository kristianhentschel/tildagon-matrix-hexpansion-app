from events import Event

class MatrixHexpansionToast(Event):
  def __init__(self, text: str = None, **kwargs):
    super()

    self.text = text
    self.options = kwargs
  
  def __str__(self):
    return "MatrixHexpansionToast"