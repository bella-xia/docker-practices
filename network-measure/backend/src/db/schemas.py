from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime


class ProbeResult(BaseModel):
    spec: str
    target: str
    success: bool 
    latency_ms: Optional[float]
    metadata: Optional[dict] = None
    ts: datetime = datetime.utcnow()

class SuccinctProbeResult(BaseModel):
    success: bool
    latency_ms: Optional[float]
    metadata: Optional[dict]

class MeasureSnapshot(BaseModel):
    ts: datetime = datetime.utcnow()
    data: Optional[Dict[str, ProbeResult]] = None

class StatusSchema(BaseModel):
    ts: datetime = datetime.utcnow()
    status: str
    target: Optional[str]

class SnapshotSchema(BaseModel):
    ts: datetime
    running: Optional[bool] = None
    data: Optional[Dict[str, SuccinctProbeResult]]

class RecentSchema(BaseModel):
    ts: datetime
    data: Optional[List[SnapshotSchema]]
