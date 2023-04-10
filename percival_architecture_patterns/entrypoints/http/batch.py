from percival_architecture_patterns.domain.models import Batch, UpdateBatch
from percival_architecture_patterns.service_layer.batch import update_existing_batch
from percival_architecture_patterns.adapters.repositories.mongo.mongo_repository import (
    MongoRepository,
)
from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

batch_router = APIRouter(
    prefix="/batches",
    tags=["batches"],
)

repo = MongoRepository()


@batch_router.post(
    "/", response_description="Create a new batch", status_code=status.HTTP_201_CREATED
)
def create_batch(request: Request, batch: Batch = Body(...)):
    return repo.create_batch(batch, request=request)


@batch_router.get(
    "/", response_description="List all batches", response_model=List[Batch]
)
def get_all_batches(request: Request):
    return repo.get_all_batches(request=request)


@batch_router.get(
    "/{reference}", response_description="Get batch by reference", response_model=Batch
)
def get_batch_by_reference(
    reference: str,
    request: Request,
):
    batch = repo.get_batch_by_reference(reference, request=request)
    if batch:
        return batch
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Batch with reference {reference} not found",
    )


@batch_router.put(
    "/{reference}", response_description="Modify existing batch", response_model=Batch
)
def update_batch_by_reference(
    reference: str,
    update_batch: UpdateBatch,
    request: Request,
):
    updated_batch = repo.update_batch_by_reference(
        reference,
        update_batch,
        request=request,
    )
    if not updated_batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"batch with reference/_id {reference} not found",
        )
    
    return updated_batch
