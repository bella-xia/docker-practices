import asyncio
import re

from .base import Probe
from ..db.schemas import ProbeResult

RTT_RE = re.compile(r'(\d+.\d+)\s*ms')

class TracerouteProbe(Probe):
    name='traceroute'

    def _parse_hop(self, line:str, expected_probes=3) -> dict:
        parts = line.split('  ')
        hop = int(parts[0])
        ips = []
        rtts = []

        for token in parts[1:]:
            if token == '*':
                rtts.append(None)
            elif token.endswith(')'):
                ips.append(token)
            else:
                m = RTT_RE.search(token)
                if m:
                    rtts.append(float(m.group(1)))
        
        return {'hop': hop, 'ips': list(set(ips)), 'rtt_ms': rtts}

    async def run(self, target:str) -> ProbeResult:
        proc = await asyncio.create_subprocess_exec(
            'traceroute', 
            # '-n',           # numeric
            '-I',           # ICMP
            '-q', '3',      # probes per hop
            '-w', '1',      # timeout
            '-m', '30',     # max hops
            target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            return ProbeResult(
                        spec=self.name,
                        target=target,
                        success=False,
                        latency_ms=None,
                        metadata={'error': stderr.decode().strip()})

        hops = []
        for line in stdout.decode().splitlines()[1:]:
            try:
                hops.append(self._parse_hop(line))
            except Exception:
                continue

        return ProbeResult(
                    spec=self.name,
                    target=target,
                    success=True,
                    latency_ms=None,
                    metadata={'nhops': len(hops),
                              'path': hops})
