from typing import Optional
from datetime import datetime
from uuid import uuid4
from backend.models.schemas import ScheduleCreate, ScheduleResponse, DailySchedule, ProgressUpdate

class ScheduleService:
    def __init__(self):
        self.schedules: dict[str, dict] = {}
    
    def create_schedule(
        self, 
        data: ScheduleCreate
    ) -> ScheduleResponse:
        from backend.algorithms.weighted_scheduler import generate_weekly_schedule
        
        schedule_id = f"sched_{uuid4().hex[:8]}"
        
        daily_schedules = generate_weekly_schedule(
            data.subjects,
            data.total_hours_per_day,
            data.total_hours_per_week
        )
        
        total_allocated = 0
        for day in daily_schedules:
            day_total = sum(a["allocated_hours"] for a in day["allocations"])
            total_allocated += day_total
        
        response = ScheduleResponse(
            id=schedule_id,
            created_at=datetime.now(),
            schedule_type=data.schedule_type,
            total_hours_per_day=data.total_hours_per_day,
            total_hours_per_week=data.total_hours_per_week,
            daily_schedules=[
                DailySchedule(
                    day=d["day"],
                    allocations=[
                        type('obj', (object,), {
                            'subject_id': a["subject_id"],
                            'subject_name': a["subject_name"],
                            'difficulty': a["difficulty"],
                            'allocated_hours': a["allocated_hours"],
                            'weight': a["weight"],
                            'deadline': None
                        })()
                        for a in d["allocations"]
                    ]
                )
                for d in daily_schedules
            ],
            total_allocated_hours=round(total_allocated, 2)
        )
        
        self.schedules[schedule_id] = {
            "data": response.model_dump(),
            "daily_allocations": daily_schedules,
            "progress": {},
            "created_at": datetime.now()
        }
        
        return response
    
    def get_schedule(self, schedule_id: str) -> Optional[dict]:
        return self.schedules.get(schedule_id)
    
    def update_progress(
        self, 
        schedule_id: str, 
        updates: list[dict]
    ) -> dict:
        if schedule_id not in self.schedules:
            return {"error": "Schedule not found"}
        
        self.schedules[schedule_id]["progress"].update({
            u["subject_id"]: u["completed_hours"] 
            for u in updates
        })
        
        return {"status": "progress updated", "schedule_id": schedule_id}
    
    def reschedule(self, schedule_id: str) -> dict:
        from backend.algorithms.dynamic_scheduler import DynamicScheduler
        
        if schedule_id not in self.schedules:
            return {"error": "Schedule not found"}
        
        sched = self.schedules[schedule_id]
        dynamic = DynamicScheduler(sched["daily_allocations"])
        
        updates_list = [
            {"subject_id": k, "completed_hours": v}
            for k, v in sched["progress"].items()
        ]
        
        if updates_list:
            for upd in updates_list:
                from backend.models.schemas import ProgressUpdate
                progress_update = ProgressUpdate(subject_id=upd["subject_id"], completed_hours=upd["completed_hours"])
                dynamic.update_progress(progress_update)
        
        new_schedule = dynamic.reschedule(remaining_days=5)
        sched["daily_allocations"] = new_schedule
        
        return {"rescheduled": True, "new_schedule": new_schedule}
    
    def get_metrics(self, schedule_id: str) -> dict:
        from backend.algorithms.dynamic_scheduler import DynamicScheduler
        
        if schedule_id not in self.schedules:
            return {"error": "Schedule not found"}
        
        sched = self.schedules[schedule_id]
        dynamic = DynamicScheduler(sched["daily_allocations"])
        
        for subj_id, hours in sched["progress"].items():
            dynamic.progress_data[subj_id] = hours
        
        return dynamic.get_efficiency_metrics(schedule_id)
    
schedule_service = ScheduleService()