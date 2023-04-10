from percival_architecture_patterns.domain.models import OrderLine, Batch
from percival_architecture_patterns.domain.utils import allocate
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

order_line_router = APIRouter(
    prefix="/order_lines",
    tags=["order_lines"],
)

@order_line_router.post("/", response_description="Create a new order_line", status_code=status.HTTP_201_CREATED)
def create_order_line(request: Request, order_line: OrderLine = Body(...)): 
    batches = [Batch.parse_obj(batch) for batch in list(request.app.database["batches"].find({}))]
    # order_line_model = OrderLine.parse_obj(order_line)
    if (batch := allocate(order_line, batches)) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No batch found that can allocate order_line {order_line}")

    request.app.database["batches"].update_one(
        {"_id": batch.reference}, {"$set": jsonable_encoder(batch)}
    )

    new_order_line = request.app.database["order_lines"].insert_one(jsonable_encoder(order_line))
    
    created_order_line = request.app.database["order_lines"].find_one(
        {"_id": new_order_line.inserted_id}
    )

    return created_order_line

@order_line_router.get("/", response_description="Get all order_lines", response_model=List[OrderLine])
def get_all_order_lines(request: Request):
    order_lines = list(request.app.database["order_lines"].find(limit=100))
    return order_lines

@order_line_router.get("/{order_id}", response_description="Get an order_line by order_id/_id")
def get_order_line(
    order_id: str,
    request: Request,
    ):
    order_line = request.app.database["order_lines"].find_one({"_id": order_id})
    if order_line is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order_line with order_id {order_id} found")
    
    return order_line

@order_line_router.delete("/{order_id}", response_description="Delete / deallocate an order_line", response_model=Batch)
def deallocate_order_line(order_id: str, request: Request, response: Response):
    if (order_line := request.app.database["order_lines"].find_one({"_id": order_id})) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order found with sku {order_line.sku}")
    
    order_line = OrderLine.parse_obj(order_line)
    batches = [Batch.parse_obj(batch) for batch in list(request.app.database["batches"].find({}))]

    for batch in batches:
        if batch.can_deallocate(order_line):
            delete_result = request.app.database["order_lines"].delete_one({"_id": order_id})
            if delete_result.deleted_count == 1:
                batch.deallocate(order_line)
                request.app.database["batches"].update_one(
                    {"_id": batch.reference}, {"$set": jsonable_encoder(batch)}
                )
                return batch
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order found with sku {order_line.sku}")