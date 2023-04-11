from typing import Optional, Set, FrozenSet, Union, List
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from percival_architecture_patterns.domain.exceptions import OutOfStock, SkuMismatch
from pydantic import BaseModel, Field
from fastapi import Request


class Frozen(BaseModel):
    class Config:
        frozen = True
        arbitrary_types_allowed = True


class OrderLine(Frozen):
    order_id: str = Field(default_factory=lambda: uuid.uuid4(), alias="_id")
    sku: str
    qty: int


class UpdateBatch(BaseModel):
    purchased_quantity: Optional[int]
    eta: Optional[datetime]
    allocations: Optional[Set[OrderLine]]


class Batch(BaseModel):
    reference: str = Field(default_factory=lambda: uuid.uuid4(), alias="_id")
    sku: str
    purchased_quantity: int
    eta: datetime = datetime.now() + timedelta(days=7)
    allocations: List[OrderLine] = []

    class Config:
        orm_mode = True

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def __gt__(self, other):
        # we override this method so we can use "sorted" on our batches
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta.timestamp() > other.eta.timestamp()

    def __hash__(self):
        return hash(self.reference)

    def can_allocate_by_sku(self, line: OrderLine) -> bool:
        return str(self.sku) == str(line.sku)

    def can_allocate_by_qty(self, line: OrderLine) -> bool:
        total_allocations = line.qty + sum(
            [order_line.qty for order_line in self.allocations]
        )
        return self.purchased_quantity >= total_allocations

    def allocate(self, line: OrderLine):
        if not self.can_allocate_by_sku(line):
            raise SkuMismatch(
                f"line sku of {line.sku} does not match batch sku of {self.sku}"
            )
        if not self.can_allocate_by_qty(line):
            raise OutOfStock(
                f"line qty of {line.qty} is larger than batch available quantity of {self.available_quantity}"
            )
        # # we convert to set, then back to frozenset, because plain sets are not hashable
        # # and thus cannot be written to our db
        if line not in self.allocations:
            self.allocations.append(line)

    def can_deallocate(self, line: OrderLine):
        print("lineee: ", line)
        print("allocationsss: ", self.allocations)
        return line in self.allocations

    def deallocate(self, line: OrderLine):
        if self.can_deallocate(line):
            self.allocations = [
                order_line for order_line in self.allocations if order_line != line
            ]

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self.allocations)

    @property
    def available_quantity(self) -> int:
        return self.purchased_quantity - self.allocated_quantity
