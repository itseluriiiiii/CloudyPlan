from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import date

@dataclass
class SubjectCreate:
    name: str
    difficulty: int
    deadline: Optional[str] = None
    
    def __post_init__(self):
        if not 1 <= self.difficulty <= 5:
            raise ValueError("Difficulty must be between 1 and 5")

@dataclass
class SubjectAllocation:
    subject_id: str
    subject_name: str
    difficulty: int
    allocated_hours: float
    weight: float
    deadline: Optional[str] = None

@dataclass
class DailySchedule:
    day: int
    allocations: List[SubjectAllocation]

@dataclass
class ScheduleResponse:
    id: str
    created_at: str
    schedule_type: str
    total_hours_per_day: float
    total_hours_per_week: float
    daily_schedules: List[DailySchedule]
    total_allocated_hours: float

@dataclass
class ProgressUpdate:
    subject_id: str
    completed_hours: float