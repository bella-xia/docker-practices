from abc import ABC, abstractmethod
from ..db.schemas import ProbeResult

class Probe(ABC):
    name: str

    @abstractmethod
    async def run(self, target: str) -> ProbeResult:
        ...
