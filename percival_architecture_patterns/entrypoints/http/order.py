from percival_architecture_patterns.domain.models import OrderLine, Batch
from percival_architecture_patterns.domain.utils import allocate
from percival_architecture_patterns.adapters.repositories.mongo.mongo_repository import MongoRepository
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

order_line_router = APIRouter(
    prefix="/order_lines",
    tags=["order_lines"],
)

repo = MongoRepository()

@order_line_router.post(
    "/",
    response_description="Create a new order_line",
    status_code=status.HTTP_201_CREATED,
)
def create_order_line(request: Request, order_line: OrderLine = Body(...)):
    created_order_line = repo.create_order_line(
        order_line,
        request=request
    )
    if not created_order_line:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No batch found that can allocate order_line {order_line}",
        )
    return created_order_line


@order_line_router.get(
    "/", response_description="Get all order_lines", response_model=List[OrderLine]
)
def get_all_order_lines(request: Request):
    return repo.get_all_order_lines(request=request)


@order_line_router.get(
    "/{order_id}", response_description="Get an order_line by order_id/_id"
)
def get_order_line_by_order_id(
    order_id: str,
    request: Request,
):
    order_line = request.app.database["order_lines"].find_one({"_id": order_id})
    if order_line is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No order_line with order_id {order_id} found",
        )

    return order_line


@order_line_router.delete(
    "/{order_id}",
    response_description="Delete / deallocate an order_line",
    response_model=Batch,
)
def deallocate_order_line(order_id: str, request: Request):
    deallocated_batch = repo.deallocate_order_line(order_id, request=request)
    if not deallocated_batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No order found for order_id {order_id}",
        )
    return deallocated_batch
