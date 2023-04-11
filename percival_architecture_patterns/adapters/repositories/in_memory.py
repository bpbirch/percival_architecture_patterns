from percival_architecture_patterns.adapters.repositories.protocols import (
    AbstractRepository,
)
from percival_architecture_patterns.domain.models import Batch, OrderLine
from percival_architecture_patterns.domain.utils import allocate
from percival_architecture_patterns.adapters.repositories.repo_params import (
    BatchParams,
    OrderParams,
)
from typing import List, Optional


class InMemoryRepository(AbstractRepository):
    def __init__(
        self,
        batches: Optional[List[Batch]] = None,
        order_lines: Optional[List[OrderLine]] = None,
    ) -> None:
        self._batches = batches or []
        self._order_lines = order_lines or []

    def create_batch(self, batch_params: BatchParams) -> Batch:
        batch = batch_params.batch
        if batch not in self._batches:
            self._batches.append(batch)
        return batch

    def update_batch_by_reference(
        self,
        batch_params: BatchParams,
    ) -> Batch:
        reference = batch_params.reference
        update_batch = batch_params.update_batch
        existing_batch = None
        for batch in self._batches:
            if str(batch.reference) == str(reference):
                existing_batch = batch
                break
        if not existing_batch:
            return None

        existing_batch.__dict__.update(update_batch)

        return existing_batch

    def allocate_order_line(
        self,
        order_params: OrderParams,
    ) -> OrderLine:
        order_line = order_params.order_line
        batches = self._batches
        if allocate(line=order_line, batches=batches) is None:
            return None
        if order_line not in self._order_lines:
            self._order_lines.append(order_line)

        return order_line

    def deallocate_order_line(
        self,
        order_params: OrderParams,
    ) -> Batch:
        order_id = order_params.order_id
        order_line = None
        found = False
        for o_line in self._order_lines:
            if str(o_line.order_id) == str(order_id):
                found = True
                order_line = o_line
        if not found:
            return None

        batches = self._batches
        for batch in batches:
            if batch.can_deallocate(order_line):
                self._order_lines.pop(self._order_lines.index(order_line))
                batch.deallocate(order_line)
                return batch
        return None

    def get_all_batches(self, batch_params: BatchParams) -> List[Batch]:
        return self._batches

    def get_batch_by_reference(self, batch_params: BatchParams) -> Batch:
        reference = batch_params.reference
        for batch in self._batches:
            if str(batch.reference) == str(reference):
                return batch

        return None

    def get_all_order_lines(self, order_params: OrderParams) -> List[OrderLine]:
        return self._order_lines

    def get_order_line_by_order_id(
        self,
        order_params: OrderParams,
    ) -> OrderLine:
        order_id = order_params.order_id
        for order_line in self._order_lines:
            if str(order_line.order_id) == str(order_id):
                return order_line

        return None
