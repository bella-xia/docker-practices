import asyncio
from datetime import datetime
from typing import List, Optional

from ..probes import Probe
from ..db.schemas import ProbeResult, MeasureSnapshot
from .state import MeasureState

class MeasureLoop:
    def __init__(self, probes: List[Probe], 
                 state: MeasureState=MeasureState(), 
                 interval_s: int=15):
        self.probes : List[Probe] = probes
        self.state: MeasureState = state
        self.interval_s: int = interval_s
        self._task: Optional[asyncio.Task] = None
        self._stop_event : asyncio.Event = asyncio.Event()

    async def start(self, target:str):
        if  self._task and not self._task.done():
            return # already running

        self.state.running = True
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run(target))

    async def _run_probe(self, probe: Probe, target: str) -> tuple[str, ProbeResult]:
        try:
            res = await probe.run(target)
        except Exception as e:
            res = ProbeResult(
                    spec=probe.name,
                    target=target,
                    success=False,
                    latency_ms=None,
                    metadata={'error': str(e)})
        return probe.name, res    

    async def _run(self, target:str):
        while not self._stop_event.is_set():
            print('starts measurement...')
            tasks = [
                self._run_probe(probe, target)
                for probe in self.probes
            ]
            res_list = await asyncio.gather(*tasks)
            results = dict(res_list)
            print('completes measurement')
            snapshot = MeasureSnapshot(ts=datetime.utcnow(),
                                       data=results)
            self.state.latest = snapshot
            if self.state.history.maxlen <= len(self.state.history) + 1:
                self.state.history.popleft()
            self.state.history.append(snapshot)

            await asyncio.sleep(self.interval_s)
