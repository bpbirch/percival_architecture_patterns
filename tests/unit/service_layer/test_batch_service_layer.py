import percival_architecture_patterns.service_layer.batch as batch_service_layer
from percival_architecture_patterns.domain.models import Batch, OrderLine, UpdateBatch
from percival_architecture_patterns.domain.exceptions import SkuMismatch, OutOfStock
from percival_architecture_patterns.adapters.repositories.in_memory import (
    InMemoryRepository,
)
import unittest
import pytest


class BatchServiceLayer(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = InMemoryRepository()

        def make_batch_and_line(batch_sku, line_sku, batch_qty, line_qty):
            return (
                Batch(
                    **{
                        "sku": batch_sku,
                        "purchased_quantity": batch_qty,
                    }
                ),
                OrderLine(**{"sku": line_sku, "qty": line_qty}),
            )

        self.matching_batch, self.matching_line = make_batch_and_line(
            "SMALL-TABLE", "SMALL-TABLE", 20, 10
        )
        self.mismatch_qty_batch, self.mismatch_qty_line = make_batch_and_line(
            "SMALL-TABLE", "SMALL-TABLE", 10, 20
        )
        self.mismatch_sku_batch, self.mismatch_sku_line = make_batch_and_line(
            "SMALL-TABLE", "BIG-LAMP", 20, 10
        )

    def test_create_batch(self) -> None:
        created_batch = batch_service_layer.create_batch(
            self.matching_batch, repo=self.repo
        )
        self.assertTrue(created_batch == self.matching_batch)
        self.assertTrue(len(self.repo._batches) == 1)
        self.assertTrue(self.repo._batches[0] == created_batch)

    def test_update_batch_by_reference(self) -> None:
        created_batch = batch_service_layer.create_batch(
            self.matching_batch, repo=self.repo
        )
        update_batch = UpdateBatch(purchased_quantity=500)
        updated_batch = batch_service_layer.update_existing_batch(
            reference=str(created_batch.reference),
            update_batch=update_batch,
            repo=self.repo,
        )
        self.assertTrue(isinstance(updated_batch, Batch))
        self.assertTrue(len(self.repo._batches) == 1)
        self.assertTrue(self.repo._batches[0].purchased_quantity == 500)

    def test_get_all_batches(self) -> None:
        batch_service_layer.create_batch(self.matching_batch, repo=self.repo)
        batch_service_layer.create_batch(self.mismatch_qty_batch, repo=self.repo)
        all_batches = batch_service_layer.get_all_batches(repo=self.repo)
        self.assertTrue(len(all_batches) == 2)

    def test_get_batch_by_reference(self) -> None:
        batch_service_layer.create_batch(self.matching_batch, repo=self.repo)
        batch = batch_service_layer.get_batch_by_reference(
            reference=str(self.matching_batch.reference),
            repo=self.repo,
        )
        self.assertTrue(batch == self.matching_batch)
