import percival_architecture_patterns.service_layer.batch as batch_service_layer
import percival_architecture_patterns.service_layer.order as order_service_layer
from percival_architecture_patterns.domain.models import Batch, OrderLine, UpdateBatch
from percival_architecture_patterns.adapters.repositories.in_memory import (
    InMemoryRepository,
)
import unittest
import pytest


class OrderServiceLayer(unittest.TestCase):
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

    def test_allocate_order_line(self) -> None:
        created_batch = batch_service_layer.create_batch(
            self.matching_batch, repo=self.repo
        )
        created_order_line = order_service_layer.allocate_order_line(
            repo=self.repo,
            order_line=self.matching_line,
        )
        self.assertEqual(created_order_line, self.matching_line)
        self.assertTrue(created_order_line in created_batch.allocations)
        self.assertTrue(created_order_line in self.repo._order_lines)

    def test_allocate_order_no_match_returns_none(self) -> None:
        created_order_line = order_service_layer.allocate_order_line(
            repo=self.repo,
            order_line=self.matching_line,
        )
        self.assertTrue(created_order_line is None)

    def test_deallocate_order_line(self) -> None:
        created_batch = batch_service_layer.create_batch(
            self.matching_batch, repo=self.repo
        )
        created_order_line = order_service_layer.allocate_order_line(
            repo=self.repo,
            order_line=self.matching_line,
        )
        self.assertEqual(created_order_line, self.matching_line)
        self.assertTrue(created_order_line in created_batch.allocations)
        batch_with_deallocation = order_service_layer.deallocate_order_line(
            order_id=str(created_order_line.order_id),
            repo=self.repo,
        )
        self.assertTrue(isinstance(batch_with_deallocation, Batch))
        self.assertTrue(created_order_line not in created_batch.allocations)
        self.assertTrue(created_order_line not in self.repo._order_lines)

    def test_get_all_order_lines(self) -> None:
        batch_service_layer.create_batch(self.matching_batch, repo=self.repo)
        created_order_line = order_service_layer.allocate_order_line(
            repo=self.repo,
            order_line=self.matching_line,
        )
        all_order_lines = order_service_layer.get_all_order_lines(repo=self.repo)
        self.assertTrue(len(all_order_lines) == 1)
        self.assertTrue(created_order_line in all_order_lines)

    def test_get_order_line_by_order_id(self) -> None:
        batch_service_layer.create_batch(self.matching_batch, repo=self.repo)
        created_order_line = order_service_layer.allocate_order_line(
            repo=self.repo,
            order_line=self.matching_line,
        )
        order_line = order_service_layer.get_order_line_by_order_id(
            order_id=str(created_order_line.order_id),
            repo=self.repo,
        )
        self.assertTrue(order_line == created_order_line)
