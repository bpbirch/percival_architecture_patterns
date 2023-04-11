from percival_architecture_patterns.domain.models import Batch, UpdateBatch
from percival_architecture_patterns.adapters.repositories.protocols import (
    AbstractRepository,
)
from percival_architecture_patterns.adapters.repositories.repo_params import BatchParams
from fastapi import Request
from typing import Optional, List


def update_existing_batch(
    reference: str,
    update_batch: UpdateBatch,
    repo: AbstractRepository,
    request: Optional[Request] = None,
) -> Batch:
    batch_params = BatchParams(
        update_batch=update_batch,
        reference=reference,
        request=request,
    )
    batch = repo.update_batch_by_reference(batch_params)
    return batch


def get_batch_by_reference(
    reference: str,
    repo: AbstractRepository,
    request: Optional[Request] = None,
) -> Batch:
    batch_params = BatchParams(reference=reference, request=request)
    batch = repo.get_batch_by_reference(batch_params)
    return batch


def get_all_batches(
    repo: AbstractRepository,
    request: Optional[Request] = None,
) -> List[Batch]:
    batch_params = BatchParams(request=request)
    return repo.get_all_batches(batch_params)


def create_batch(
    batch: Batch,
    repo: AbstractRepository,
    request: Optional[Request] = None,
) -> Batch:
    batch_params = BatchParams(batch=batch, request=request)
    batch = repo.create_batch(batch_params)
    return batch
