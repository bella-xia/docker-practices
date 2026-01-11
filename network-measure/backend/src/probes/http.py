import httpx
import time

from .base import Probe
from ..db.schemas import ProbeResult


class HTTPProbe(Probe):
    name='http'

    def __init__(self, scheme:str='http'):
        self.scheme = scheme
        self.name = scheme

    def _normalize(self, target:str) -> str:
        if not target.startswith((f'{self.scheme}://')):
            return f'{self.scheme}://' + target
        return target

    async def run(self, target:str) -> ProbeResult:
        
        target = self._normalize(target)
        timings = {}

        async def on_request_start():
            timings['start'] = time.perf_counter_ns()


        async def on_response_headers():
            timings['ttfb'] = time.perf_counter_ns()

        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=httpx.Timeout(5.0),
                event_hooks={
                        'request': [lambda _: on_request_start()],
                        'response': [lambda _: on_response_headers()],
                    },
            ) as client:
                resp = await client.get(target)
                end = time.perf_counter_ns()
        
            start = timings['start']
            ttfb = timings.get('ttfb', end)

            return ProbeResult(
                spec=self.name,
                target=target,
                success=True,
                latency_ms=(end-start) / 1e6,
                metadata={
                        'ttfb_ms': (ttfb-start) / 1e6,
                        'content_ms': (end-ttfb) / 1e6,
                        'status': resp.status_code,
                        'bytes': len(resp.content),})
        
        except Exception as e:
            return ProbeResult(
                spec=self.name,
                target=target,
                success=False,
                latency_ms=None,
                metadata={'error': str(e)})
