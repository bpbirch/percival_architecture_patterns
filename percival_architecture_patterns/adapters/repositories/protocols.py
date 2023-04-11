from typing import Protocol, runtime_checkable, List
from percival_architecture_patterns.domain.models import OrderLine, Batch
from percival_architecture_patterns.adapters.repositories.repo_params import (
    OrderParams,
    BatchParams,
)


@runtime_checkable
class AbstractWriteRepository(Protocol):
    def create_batch(self, batch_params: BatchParams) -> Batch:
        """Add a batch"""

    def update_batch_by_reference(self, batch_params: BatchParams) -> Batch:
        """Update existing batch"""

    def allocate_order_line(self, order_params: OrderParams) -> OrderLine:
        """Create an order_line"""

    def deallocate_order_line(self, order_params: OrderParams) -> Batch:
        """Deallocate an order line"""


@runtime_checkable
class AbstractReadRepository(Protocol):
    def get_all_batches(self, batch_params: BatchParams) -> List[Batch]:
        """Get all batches"""

    def get_batch_by_reference(self, batch_params: BatchParams) -> Batch:
        """Get batch by reference ID"""

    def get_all_order_lines(self, order_params: OrderParams):
        """Get all order_lines"""

    def get_order_line_by_order_id(self, order_params: OrderParams) -> OrderLine:
        """Get order_line by order_id"""


@runtime_checkable
class AbstractRepository(AbstractWriteRepository, AbstractReadRepository, Protocol):
    pass
