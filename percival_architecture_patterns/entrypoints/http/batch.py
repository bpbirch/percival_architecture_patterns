from percival_architecture_patterns.domain.models import Batch, UpdateBatch
from percival_architecture_patterns.service_layer.batch import update_existing_batch
from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

batch_router = APIRouter(
    prefix="/batch",
    tags=["batch"],
)

@batch_router.post("/", response_description="Create a new batch", status_code=status.HTTP_201_CREATED)
def create_batch(request: Request, batch: Batch = Body(...)):
    batch = jsonable_encoder(batch)
    new_batch = request.app.database["batches"].insert_one(batch)

    created_batch = request.app.database["batches"].find_one(
        {"_id": new_batch.inserted_id}
    )

    return created_batch

@batch_router.get("/", response_description="List all batches", response_model=List[Batch])
def get_all_batches(request: Request):
    batches = list(request.app.database["batches"].find(limit=100))
    return batches

@batch_router.get("/{reference}", response_description="Get batch by reference", response_model=Batch)
def get_batch_by_reference(
    reference: str,
    request: Request,
    ):
    if (batch := request.app.database["batches"].find_one({"_id": reference})) is not None:
        return batch
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch with reference {reference} not found")

@batch_router.put("/{reference}", response_description="Modify existing batch", response_model=Batch)
def modify_batch(
    reference: str,
    update_batch: UpdateBatch,
    request: Request,
    ):
    if (existing_batch := request.app.database["batches"].find_one({"_id": reference})) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"batch with reference/_id {reference} not found")
    else:
        existing_batch = Batch.parse_obj(existing_batch)
        updated_existing_batch = update_existing_batch(existing_batch, update_batch)
        updated_existing_batch = jsonable_encoder(updated_existing_batch)

    update_result = request.app.database["batches"].update_one(
        {"_id": reference}, {"$set": updated_existing_batch}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"batch with reference/_id {reference} not found")
    
    if (
        updated_batch := request.app.database["batches"].find_one({"_id": reference})
    ) is not None:
        return updated_batch
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"batch with reference/_id {reference} not found")