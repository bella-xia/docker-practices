from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query

from ..core.loop import MeasureLoop
from ..db.schemas import (ProbeResult, SuccinctProbeResult,
                          StatusSchema, SnapshotSchema, RecentSchema)
from ..probes import (Probe,
                      PingProbe, DNSProbe,  
                      TCPProbe, TLSProbe,
                      HTTPProbe, TracerouteProbe)

router: APIRouter = APIRouter()
_loop: Optional[MeasureLoop] = None
_trace: Optional[Probe] = None

def init_loop():
    global _loop, _trace
    _loop = MeasureLoop(probes=[
            PingProbe(), DNSProbe(),
            TCPProbe(port=443), TLSProbe(port=443),
            HTTPProbe(scheme='http'),
            HTTPProbe(scheme='https')
        ])
    _trace = TracerouteProbe()
    print('initialized loop')

@router.post('/start', response_model=StatusSchema)
async def start_measure(target:str='google.com'):
    global _loop
    await _loop.start(target)
    return StatusSchema(status='started', target=target)
    
@router.post('/pause', response_model=StatusSchema)
async def pause_measure():
    global _loop
    _loop.state.running = False
    if _loop._task:
        _loop._task.cancel()
    return StatusSchema(status='paused', target=None)

@router.post('/clear', response_model=StatusSchema)
async def clear_measure():
    global _loop
    _loop.state.running = False
    _loop.state.latest = None
    _loop.state.history.clear()
    if _loop._task:
        _loop._task.cancel()
    return StatusSchema(status='cleared', target=None)

@router.get('/snapshot', response_model=SnapshotSchema)
async def get_snapshot():
    global _loop
    if not _loop.state.latest:
        return SnapshotSchema(
                    ts=datetime.utcnow(),
                    running=_loop.state.running,
                    data=None)

    return SnapshotSchema(
                ts=_loop.state.latest.ts,
                running=_loop.state.running,
                data=
                {name: 
                    SuccinctProbeResult(
                        latency_ms=r.latency_ms,
                        success=r.success,
                        metadata=r.metadata)
                 for name, r in _loop.state.latest.data.items()})

@router.get('/recent', response_model=RecentSchema)
async def get_recent(k: int=Query(default=30), 
                     ps: Optional[List[str]]=Query(default=None)):
    global _loop 
    avail_k = min(k, len(_loop.state.history))
    if avail_k == 0 or ps is None or len(ps) == 0:
        return RecentSchema(ts=datetime.utcnow(), data=None)

    data: List[ShapshotSchema] = []
    for entry in list(_loop.state.history)[-avail_k:]:
        item = SnapshotSchema(
                    ts=entry.ts,
                    data={
                        name: SuccinctProbeResult(
                            latency_ms=r.latency_ms,
                            success=r.success,
                            metadata=r.metadata)
                     for name, r in entry.data.items() if name in ps})
        data.append(item)
    
    return RecentSchema(ts=_loop.state.latest.ts, data=data)

@router.get('/traceroute', response_model=ProbeResult)
async def get_traceroute(target: str = 'google.com'):
    global _trace
    return await _trace.run(target)
