import asyncio
import socket
import time

from .base import Probe
from ..db.schemas import ProbeResult

class TCPProbe(Probe):
    name='tcp_connect'

    def __init__(self, port: int, timeout: float=1.0):
        self.port = port
        self.timeout = timeout

    async def run(self, target: str) -> ProbeResult:
        start = time.perf_counter_ns()
        try:
            with socket.create_connection((target, self.port), 
                            timeout=self.timeout) as sock: 
    
                end = time.perf_counter_ns()

                return ProbeResult(
                        spec=self.name,
                        target=f'{target}:{self.port}',
                        success=True,
                        latency_ms=(end-start) / 1e6)

        except Exception as e:
            return ProbeResult(
                        spec=self.name,
                        target=f'{target}:{self.port}',
                        success=False,
                        latency_ms=None,
                        metadata={'error': str(e)})
