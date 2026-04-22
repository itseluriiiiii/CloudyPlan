from fastapi import APIRouter, HTTPException, status
from typing import Optional
from backend.models.schemas import (
    ScheduleCreate,
    ScheduleResponse,
    ProgressUpdate,
    RescheduleRequest,
    MetricsResponse
)
from backend.services.schedule_service import schedule_service

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.post("/generate", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(data: ScheduleCreate):
    return schedule_service.create_schedule(data)

@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str):
    sched = schedule_service.get_schedule(schedule_id)
    if not sched:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return sched["data"]

@router.put("/{schedule_id}/progress")
async def update_progress(schedule_id: str, updates: list[ProgressUpdate]):
    result = schedule_service.update_progress(
        schedule_id,
        [u.model_dump() for u in updates]
    )
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    return result

@router.post("/{schedule_id}/reschedule")
async def reschedule(schedule_id: str, request: Optional[RescheduleRequest] = None):
    result = schedule_service.reschedule(schedule_id)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    return result

@router.get("/{schedule_id}/metrics")
async def get_metrics(schedule_id: str):
    metrics = schedule_service.get_metrics(schedule_id)
    if "error" in metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=metrics["error"]
        )
    return metrics