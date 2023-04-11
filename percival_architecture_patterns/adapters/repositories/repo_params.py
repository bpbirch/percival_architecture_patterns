from percival_architecture_patterns.domain.models import Batch, OrderLine, UpdateBatch
from pydantic import BaseModel
from typing import Optional
from fastapi import Request


class OrderParams(BaseModel):
    order_line: Optional[OrderLine]
    order_id: Optional[str]
    request: Optional[Request]

    class Config:
        frozen = True
        arbitrary_types_allowed = True


class BatchParams(BaseModel):
    batch: Optional[Batch]
    update_batch: Optional[UpdateBatch]
    reference: Optional[str]
    request: Optional[Request]

    class Config:
        frozen = True
        arbitrary_types_allowed = True
