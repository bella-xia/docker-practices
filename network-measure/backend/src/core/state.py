from collections import deque
from ..db.schemas import MeasureSnapshot

class MeasureState:
    def __init__(self, max_history=30):
        self.running=False
        self.latest: MeasureSnapshot | None = None
        self.history: deque[MeasureSnapshot] = deque(maxlen=max_history)
