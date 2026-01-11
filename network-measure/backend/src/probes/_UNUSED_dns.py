import socket
import time
from typing import List

from .base import Probe
from ..db.schemas import ProbeResult

class UNUSEDDNSProbe(Probe):
    name='dns'

    async def run(self, target:str) -> ProbeResult:
        start = time.perf_counter_ns()
        try:
            infos = socket.getaddrinfo(
                                target, None,
                                proto=socket.IPPROTO_TCP)
            end = time.perf_counter_ns()
            ips = list({info[4][0] for info in infos})
            return ProbeResult(
                        spec=self.name,
                        target=target,
                        success=True,
                        latency_ms=(end-start) / 1e6,
                        metadata={'ips': ips})

        except Exception as e:
            return ProbeResult(
                        spec=self.name,
                        target=target,
                        success=False,
                        latency_ms=None,
                        metadata={'error': str(e)})
