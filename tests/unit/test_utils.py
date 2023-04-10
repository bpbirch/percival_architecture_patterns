from percival_architecture_patterns.domain.models import Batch, OrderLine
from percival_architecture_patterns.domain.utils import allocate
import unittest
from datetime import datetime, timedelta
import pytest


class UtilTester(unittest.TestCase):
    def test_allocating_reduces_batch_avl_qty(self) -> None:
        early_batch = Batch(
            **{
                "reference": "12345",
                "sku": "MEDIUM-TABLE",
                "purchased_quantity": 20,
                "eta": datetime.now() + timedelta(days=2),
            }
        )
        late_batch = Batch(
            **{
                "reference": "12345",
                "sku": "MEDIUM-TABLE",
                "purchased_quantity": 20,
                "eta": datetime.now() + timedelta(days=5),
            }
        )
        line = OrderLine(
            **{
                "sku": "MEDIUM-TABLE",
                "qty": 10,
            }
        )

        allocation_batch = allocate(line, [late_batch, early_batch])

        self.assertTrue(allocation_batch == early_batch)
