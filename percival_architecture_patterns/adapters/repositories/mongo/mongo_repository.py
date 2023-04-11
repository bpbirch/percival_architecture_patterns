from percival_architecture_patterns.adapters.repositories.protocols import (
    AbstractRepository,
)
from percival_architecture_patterns.domain.models import Batch, OrderLine
from percival_architecture_patterns.domain.utils import allocate
from percival_architecture_patterns.adapters.repositories.repo_params import (
    BatchParams,
    OrderParams,
)
from typing import List
from fastapi.encoders import jsonable_encoder


class MongoRepository(AbstractRepository):
    def create_batch(self, batch_params: BatchParams) -> Batch:
        raw_batch = batch_params.batch
        request = batch_params.request
        batch = jsonable_encoder(raw_batch)
        new_batch = request.app.database["batches"].insert_one(batch)

        created_batch = request.app.database["batches"].find_one(
            {"_id": new_batch.inserted_id}
        )

        return created_batch

    def update_batch_by_reference(self, batch_params: BatchParams) -> Batch:
        reference = batch_params.reference
        request = batch_params.request
        update_batch = batch_params.update_batch
        if (
            existing_batch := request.app.database["batches"].find_one(
                {"_id": reference}
            )
        ) is None:
            return None
        update_batch = {k: v for k, v in update_batch if v is not None}
        existing_batch = Batch.parse_obj(existing_batch)
        existing_batch.__dict__.update(update_batch)
        # updated_existing_batch = update_existing_batch(existing_batch, update_batch)
        updated_existing_batch = jsonable_encoder(existing_batch)

        update_result = request.app.database["batches"].update_one(
            {"_id": reference}, {"$set": updated_existing_batch}
        )
        if update_result.modified_count == 0:
            return None

        return request.app.database["batches"].find_one({"_id": reference})

    def allocate_order_line(self, order_params: OrderParams) -> OrderLine:
        request = order_params.request
        order_line = order_params.order_line
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

    def deallocate_order_line(self, order_params: OrderParams) -> Batch:
        order_id = order_params.order_id
        request = order_params.request
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

        return None

    def get_all_batches(self, batch_params: BatchParams) -> List[Batch]:
        request = batch_params.request
        batches = list(request.app.database["batches"].find(limit=100))
        return batches

    def get_batch_by_reference(self, batch_params: BatchParams) -> Batch:
        reference = batch_params.reference
        request = batch_params.request
        return request.app.database["batches"].find_one({"_id": reference})

    def get_all_order_lines(self, order_params: OrderParams) -> List[OrderLine]:
        request = order_params.request
        return list(request.app.database["order_lines"].find(limit=100))

    def get_order_line_by_order_id(self, order_params: OrderParams) -> OrderLine:
        order_id = order_params.order_id
        request = order_params.request
        return request.app.database["order_lines"].find_one({"_id": order_id})
