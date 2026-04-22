from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SubjectCreate:
    name: str # Using 'name' but can be mapped to subject_identity
    difficulty: int
    deadline: Optional[str] = None
    
    def __post_init__(self):
        if not 1 <= self.difficulty <= 5:
            raise ValueError("Difficulty must be between 1 and 5")

@dataclass
class ScheduleCreate:
    subjects: List[Dict[str, Any]]
    total_hours_per_day: float
    total_hours_per_week: float
    schedule_type: str = "weekly"

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
    day_name: str
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
    
    def dict(self):
        return asdict(self)

@dataclass
class ProgressUpdate:
    subject_id: str
    completed_hours: float