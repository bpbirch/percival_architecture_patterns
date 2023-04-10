from percival_architecture_patterns.domain.models import OrderLine, Batch
from typing import List


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    sorted_batches = sorted(batches)
    for batch in sorted_batches:
        if batch.can_allocate_by_qty(line) and batch.can_allocate_by_sku(line):
            batch.allocate(line)
            return batch
    return None
