from percival_architecture_patterns.domain.models import Batch, UpdateBatch
from percival_architecture_patterns.adapters.repositories.mongo.mongo_repository import (
    MongoRepository,
)
from fastapi import APIRouter, Body, Request, HTTPException, status
from typing import List
import percival_architecture_patterns.service_layer.batch as batch_service_layer

batch_router = APIRouter(
    prefix="/batches",
    tags=["batches"],
)

repo = MongoRepository()


@batch_router.post(
    "/", response_description="Create a new batch", status_code=status.HTTP_201_CREATED
)
def create_batch(request: Request, batch: Batch = Body(...)):
    return batch_service_layer.create_batch(
        batch=batch,
        repo=repo,
        request=request,
    )


@batch_router.get(
    "/", response_description="List all batches", response_model=List[Batch]
)
def get_all_batches(request: Request):
    return batch_service_layer.get_all_batches(repo=repo, request=request)


@batch_router.get(
    "/{reference}", response_description="Get batch by reference", response_model=Batch
)
def get_batch_by_reference(
    reference: str,
    request: Request,
):
    batch = batch_service_layer.get_batch_by_reference(
        reference=reference, repo=repo, request=request
    )
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with reference {reference} not found",
        )
    return batch


@batch_router.put(
    "/{reference}", response_description="Modify existing batch", response_model=Batch
)
def update_batch_by_reference(
    reference: str,
    update_batch: UpdateBatch,
    request: Request,
):
    updated_batch = batch_service_layer.update_existing_batch(
        reference=reference,
        update_batch=update_batch,
        repo=repo,
        request=request,
    )
    if not updated_batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"batch with reference/_id {reference} not found",
        )

    return updated_batch
