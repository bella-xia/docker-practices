import dns.resolver
import time

from .base import Probe
from ..db.schemas import ProbeResult

class DNSProbe(Probe):
    name='dns'

    async def run(self, target:str) -> ProbeResult:
        
        start=time.perf_counter_ns()
        resolver = dns.resolver.Resolver()

        try:
            answer = resolver.resolve(target, 'A')
            end = time.perf_counter_ns()

            ips = [r.address for r in answer]

            return ProbeResult(
                spec=self.name,
                target=target,
                success=True,
                latency_ms=(end-start) / 1e6,
                metadata={'ips': ips})

        except dns.resolver.NXDOMAIN:
            return ProbeResult(
                spec=self.name,
                target=target,
                success=False,
                latency_ms=None,
                metadata={'error': 'NXDOMAIN'})

        except dns.resolver.Timeout:
            return ProbeResult(
                spec=self.name,
                target=target,
                success=False,
                latency_ms=None,
                metadata={'error': 'TIMEOUT'})

        except dns.resolver.NoNameservers:
            return ProbeResult(
                spec=self.name,
                target=target,
                success=False,
                latency_ms=None,
                metadata={'error': 'NO_NAMESERVERS'})
        
        except Exception as e:
            return ProbeResult(
                spec=self.name,
                target=target,
                success=False,
                latency_ms=None,
                metadata={'error': str(e)}
            )
