from typing import Protocol, runtime_checkable, List, Optional
from percival_architecture_patterns.domain.models import OrderLine, Batch, UpdateBatch
from fastapi import Request


@runtime_checkable
class AbstractWriteRepository(Protocol):
    def create_batch(self, batch: Batch, request: Optional[Request]) -> Batch:
        """Add a batch"""

    def update_batch(
        self, reference: str, update_batch: UpdateBatch, reqeust: Optional[Request]
    ) -> Batch:
        """Update existing batch"""

    def create_order_line(
        self, order_line: OrderLine, request: Optional[Request]
    ) -> OrderLine:
        """Create an order_line"""

    def deallocate_order_line(self, order_id: str, request: Optional[Request]) -> Batch:
        """Deallocate an order line"""


@runtime_checkable
class AbstractReadRepository(Protocol):
    def get_all_batches(self, request: Optional[Request]) -> List[Batch]:
        """Get all batches"""

    def get_batch_by_reference(
        self, reference: str, request: Optional[Request]
    ) -> Batch:
        """Get batch by reference ID"""

    def get_all_order_lines(self, request: Optional[Request]):
        """Get all order_lines"""

    def get_order_line_by_order_id(
        self, order_id: str, request: Optional[Request]
    ) -> OrderLine:
        """Get order_line by order_id"""


@runtime_checkable
class AbstractRepository(AbstractWriteRepository, AbstractReadRepository, Protocol):
    pass
