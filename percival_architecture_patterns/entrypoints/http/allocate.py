from fastapi import APIRouter, Depends, status, Body, Request
from dependency_injector.wiring import Provide, inject
from percival_architecture_patterns.domain.models import Batch

allocate_router = APIRouter(
    prefix="/allocate",
    tags=["allocate"],
)

@allocate_router.post(
    "/",
    response_class="Create a new Batch",
    status_code=status.HTTP_201_CREATED,
    response_model=Batch)