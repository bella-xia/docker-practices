from typing import Optional, Annotated, List
from pydantic import BaseModel, Field 
from pydantic.functional_validators import BeforeValidator
from bson import ObjectId
from datetime import datetime

# database model
class DocumentModel(BaseModel):
    id: Optional[Annotated[str, BeforeValidator(str)]] = Field(alias='_id', default=None)
    text: str = Field(default='')
    embed: Optional[List[float]] = Field(default=None)
    metadata: Optional[dict] = Field(default=None)
    status: Optional[str] =Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    modified_at: Optional[datetime] = Field(default=None)

# schema for network services
class QuerySchema(BaseModel):
    text: str
    top_k: int = 10

class ResponseSchema(BaseModel):
    id: Optional[Annotated[str, BeforeValidator(str)]] = Field(alias='_id', default=None)
    text: str = Field(default='')
    score: float = Field(default=0.0)
    metadata: Optional[dict] = Field(default=None)

class ViewableDocumentSchema(BaseModel): # masking embedding on users
    id: Optional[Annotated[str, BeforeValidator(str)]] = Field(alias='_id', default=None)
    text: str = Field(default='')
    metadata: Optional[dict] = Field(default=None)
    status: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    modified_at: Optional[datetime] = Field(default=None)

class CustomDocumentSchema(BaseModel): # masking fields users should not change
    text: str = Field(default='')
    metadata: Optional[dict] = Field(default=None)

class StatsSchema(BaseModel):
    total: int = Field(default=0)
    ready: int = Field(default=0)
    processing: int = Field(default=0)
    error: int = Field(default=0)
    embedded_ratio: float = Field(default=0.0)
    indexed_ratio: float = Field(default=0.0) 
