from percival_architecture_patterns.domain.models import Batch, UpdateBatch

def update_existing_batch(batch: Batch, update_batch: UpdateBatch) -> Batch:
    update_batch = {k:v for k, v in update_batch if v is not None}
    batch.__dict__.update(update_batch)
    return batch