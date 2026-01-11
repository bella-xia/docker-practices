import time
import ssl
import socket
from datetime import datetime

from .base import Probe
from ..db.schemas import ProbeResult

class TLSProbe(Probe):
    name='tls_handshake'
    
    def __init__(self, port:int, timeout:float=3.0):
        self.port = port
        self.timeout = timeout

    async def run(self, target:str) -> ProbeResult:
        
        try:
            with socket.create_connection((target, self.port), 
                            timeout=self.timeout) as sock: 
                start = time.perf_counter_ns()
                ctx = ssl.create_default_context()
            
                with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                    end = time.perf_counter_ns()
                    cert = ssock.getpeercert()
                    expires = datetime.strptime(
                        cert['notAfter'],
                        '%b %d %H:%M:%S %Y %Z'
                    )

                    return ProbeResult(
                        spec=self.name,
                        target=f'{target}:{self.port}',
                        success=True,
                        latency_ms=(end-start)/ 1e6,
                        metadata={
                                'tls_version': ssock.version(),
                                'cipher': ssock.cipher()[0],
                                'cert_expires_days': (expires - datetime.utcnow()).days })

        except Exception as e:
            return ProbeResult(
                        spec=self.name,
                        target=f'{target}:{self.port}',
                        success=False,
                        latency_ms=None,
                        metadata={'error': str(e)})
