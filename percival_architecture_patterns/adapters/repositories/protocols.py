from typing import Protocol, runtime_checkable
from percival_architecture_patterns.domain.models import OrderLine, Batch

@runtime_checkable
class BatchWriteRepository(Protocol):
    async def allocate(self, line: OrderLine) -> None:
        """You can allocate an orderline"""

    async def deallocate(self, line: OrderLine, batch: Batch) -> None:
        """You can deallcate an orderline from a batch"""

@runtime_checkable
class BatchReadRepository(Protocol):
    async def get_allocations_for_batch(self, batch_ref: str) -> None:
        """You can get the allocations for a batch based on its reference"""
