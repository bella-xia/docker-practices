import asyncio
import re
import statistics
import time

from .base import Probe
from ..db.schemas import ProbeResult

class PingProbe(Probe):
    name='ping'

    def __init__(self, count:int = 1):
        self.count = count

    async def run(self, target:str) -> ProbeResult:

        try:
            proc = await asyncio.create_subprocess_exec(
                'ping', '-c', str(self.count), '-n', target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                return ProbeResult(
                    spec=self.name,
                    target=target,
                    success=False,
                    latency_ms=None,
                    error=stderr.decode())

            rtts = []
            for line in stdout.decode().splitlines():
                if 'time=' in line:
                    m = re.search(r'time=([\d.]+)', line)
                    if m:
                        rtts.append(float(m.group(1)))

            received = len(rtts)

            if received == 0:
                return ProbeResult(
                            spec=self.name,
                            target=target,
                            success=False,
                            latency_ms=None,
                            metadata={
                                    'sent': self.count,
                                    'received': received,
                                    'error': 'all packets lost',
                                })

            return ProbeResult(
                        spec=self.name,
                        target=target,
                        success=True,
                        latency_ms=rtts[0] if received == 1 else sum(rtts) / received,
                        metadata={
                                'sent': self.count,
                                'received': received,
                                'lost': self.count - received,
                                'min_ms': min(rtts),
                                'avg_ms': rtts[0] if received == 1 else sum(rtts) / received,
                                'max_ms': max(rtts),
                                'jitter_ms': 0 if received == 1 else statistics.pstdev(rtts)

                            })

        except Exception as e:
            return ProbeResult(
                spec=self.name,
                target=target,
                success=False,
                latency_ms=None,
                metadata={'error': str(e)})
