from percival_architecture_patterns.domain.models import OrderLine, Batch
from percival_architecture_patterns.adapters.repositories.protocols import (
    AbstractRepository,
)
from percival_architecture_patterns.adapters.repositories.repo_params import OrderParams
from fastapi import Request
from typing import Optional, List


def allocate_order_line(
    repo: AbstractRepository,
    order_line: OrderLine,
    request: Optional[Request] = None,
) -> OrderLine:
    order_params = OrderParams(order_line=order_line, request=request)
    return repo.allocate_order_line(order_params)


def deallocate_order_line(
    order_id: str,
    repo: AbstractRepository,
    request: Optional[Request] = None,
) -> Batch:
    order_params = OrderParams(order_id=order_id, request=request)
    deallocated_batch = repo.deallocate_order_line(
        order_params,
    )
    return deallocated_batch


def get_all_order_lines(
    repo: AbstractRepository,
    request: Optional[Request] = None,
) -> List[OrderLine]:
    order_params = OrderParams(request=request)
    return repo.get_all_order_lines(order_params)


def get_order_line_by_order_id(
    order_id: str,
    repo: AbstractRepository,
    request: Optional[Request] = None,
) -> OrderLine:
    order_params = OrderParams(order_id=order_id, request=request)
    return repo.get_order_line_by_order_id(
        order_params,
    )
