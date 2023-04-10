from percival_architecture_patterns.domain.models import Batch, OrderLine
from percival_architecture_patterns.domain.exceptions import SkuMismatch, OutOfStock
import unittest
import pytest

class BatchTester(unittest.TestCase):

    def setUp(self) -> None:
        def make_batch_and_line(batch_sku, line_sku, batch_qty, line_qty):
            return (
                Batch(**{
                    "sku": batch_sku,
                    "purchased_quantity": batch_qty,
                }),
                OrderLine(**{
                "sku": line_sku,
                "qty": line_qty
                }),
            )
        
        self.matching_batch, self.matching_line = make_batch_and_line("SMALL-TABLE", "SMALL-TABLE", 20, 10)
        self.mismatch_qty_batch, self.mismatch_qty_line = make_batch_and_line("SMALL-TABLE", "SMALL-TABLE", 10, 20)
        self.mismatch_qty_batch.reference = self.matching_batch.reference
        self.mismatch_sku_batch, self.mismatch_sku_line = make_batch_and_line("SMALL-TABLE", "BIG-LAMP", 20, 10)

    def test_allocating_reduces_batch_avl_qty(self) -> None:
        self.matching_batch.allocate(self.matching_line)
        self.assertTrue(self.matching_batch.available_quantity == 10)

    def test_can_allocate_by_sku(self) -> None:
        self.assertTrue(self.matching_batch.can_allocate_by_sku(self.matching_line) == True)
        self.assertFalse(self.mismatch_sku_batch.can_allocate_by_sku(self.mismatch_sku_line) == True)

    def test_can_allocate_by_qty(self) -> None:
        self.assertTrue(self.matching_batch.can_allocate_by_qty(self.matching_line) == True)
        self.assertFalse(self.mismatch_qty_batch.can_allocate_by_qty(self.mismatch_qty_line) == True)

    def test_allocating_too_much_qty_raises_value_error(self) -> None:
        with pytest.raises(OutOfStock) as error_info:
            self.mismatch_qty_batch.allocate(self.mismatch_qty_line)

        self.assertTrue(
            str(error_info.value)  # type: ignore
            == f'line qty of {self.mismatch_qty_line.qty} is larger than batch available quantity of {self.mismatch_qty_batch.available_quantity}'
        )

    def test_allocating_with_mismatch_sku_raises_value_error(self) -> None:
        with pytest.raises(SkuMismatch) as error_info:
            self.mismatch_sku_batch.allocate(self.mismatch_sku_line)

        self.assertTrue(
            str(error_info.value)
            == f'line sku of {self.mismatch_sku_line.sku} does not match batch sku of {self.mismatch_sku_batch.sku}'
        )

    def test_allocation_idempotecy(self) -> None:
        self.matching_batch.allocate(self.matching_line)
        self.assertTrue(self.matching_batch.available_quantity == 10)
        self.matching_batch.allocate(self.matching_line)
        self.assertTrue(self.matching_batch.available_quantity == 10)

    def test_eq(self) -> None:
        self.assertTrue(self.matching_batch == self.mismatch_qty_batch)