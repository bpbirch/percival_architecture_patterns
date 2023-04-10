from percival_architecture_patterns.adapters.repositories.protocols import (
    AbstractRepository,
)
from percival_architecture_patterns.service_layer.batch import update_existing_batch
from percival_architecture_patterns.domain.models import Batch, OrderLine, UpdateBatch
from percival_architecture_patterns.domain.utils import allocate
from typing import Optional, List
from fastapi import Request
from fastapi.encoders import jsonable_encoder


class MongoRepository(AbstractRepository):
    def create_batch(self, batch: Batch, request: Optional[Request]) -> Batch:
        batch = jsonable_encoder(batch)
        new_batch = request.app.database["batches"].insert_one(batch)

        created_batch = request.app.database["batches"].find_one(
            {"_id": new_batch.inserted_id}
        )

        return created_batch

    def update_batch_by_reference(
        self, reference: str, update_batch: UpdateBatch, request: Optional[Request]
    ) -> Batch:
        if (
            existing_batch := request.app.database["batches"].find_one(
                {"_id": reference}
            )
        ) is None:
            return None

        existing_batch = Batch.parse_obj(existing_batch)
        updated_existing_batch = update_existing_batch(existing_batch, update_batch)
        updated_existing_batch = jsonable_encoder(updated_existing_batch)

        update_result = request.app.database["batches"].update_one(
            {"_id": reference}, {"$set": updated_existing_batch}
        )
        if update_result.modified_count == 0:
            return None

        return request.app.database["batches"].find_one({"_id": reference})

    def create_order_line(
        self, order_line: OrderLine, request: Optional[Request]
    ) -> OrderLine:
        batches = [
            Batch.parse_obj(batch)
            for batch in list(request.app.database["batches"].find({}))
        ]

        if (batch := allocate(order_line, batches)) is None:
            return None

        request.app.database["batches"].update_one(
            {"_id": batch.reference}, {"$set": jsonable_encoder(batch)}
        )

        new_order_line = request.app.database["order_lines"].insert_one(
            jsonable_encoder(order_line)
        )

        created_order_line = request.app.database["order_lines"].find_one(
            {"_id": new_order_line.inserted_id}
        )

        return created_order_line

    def deallocate_order_line(self, order_id: str, request: Optional[Request]) -> Batch:
        if (
            order_line := request.app.database["order_lines"].find_one(
                {"_id": order_id}
            )
        ) is None:
            return None

        order_line = OrderLine.parse_obj(order_line)
        batches = [
            Batch.parse_obj(batch)
            for batch in list(request.app.database["batches"].find({}))
        ]

        for batch in batches:
            if batch.can_deallocate(order_line):
                delete_result = request.app.database["order_lines"].delete_one(
                    {"_id": order_id}
                )
                if delete_result.deleted_count == 1:
                    batch.deallocate(order_line)
                    request.app.database["batches"].update_one(
                        {"_id": batch.reference}, {"$set": jsonable_encoder(batch)}
                    )
                    return batch
                return None

    def get_all_batches(self, request: Optional[Request]) -> List[Batch]:
        batches = list(request.app.database["batches"].find(limit=100))
        return batches

    def get_batch_by_reference(
        self, reference: str, request: Optional[Request]
    ) -> Batch:
        return request.app.database["batches"].find_one({"_id": reference})

    def get_all_order_lines(self, request: Optional[Request]):
        return list(request.app.database["order_lines"].find(limit=100))

    def get_order_line_by_order_id(
        self, order_id: str, request: Optional[Request]
    ) -> OrderLine:
        return request.app.database["order_lines"].find_one({"_id": order_id})
