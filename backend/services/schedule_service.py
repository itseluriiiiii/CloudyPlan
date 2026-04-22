from typing import Optional, List, Dict
from datetime import datetime
from uuid import uuid4
from models.schemas import ScheduleCreate, ScheduleResponse, DailySchedule, SubjectAllocation

class ScheduleService:
    def __init__(self):
        self.schedules: Dict[str, Dict] = {}
    
    def create_schedule(
        self, 
        data: ScheduleCreate
    ) -> ScheduleResponse:
        from algorithms.weighted_scheduler import generate_weekly_schedule
        
        schedule_id = f"sched_{uuid4().hex[:8]}"
        
        daily_schedules = generate_weekly_schedule(
            data.subjects,
            data.total_hours_per_day,
            data.total_hours_per_week
        )
        
        total_allocated = 0
        formatted_days = []
        
        for d in daily_schedules:
            allocs = []
            for a in d["allocations"]:
                total_allocated += a["allocated_hours"]
                allocs.append(SubjectAllocation(
                    subject_id=a["subject_id"],
                    subject_name=a["subject_name"],
                    difficulty=a["difficulty"],
                    allocated_hours=a["allocated_hours"],
                    weight=a["weight"],
                    deadline=a.get("deadline")
                ))
            
            formatted_days.append(DailySchedule(
                day=d["day"],
                day_name=d["day_name"],
                allocations=allocs
            ))
        
        response = ScheduleResponse(
            id=schedule_id,
            created_at=datetime.now().isoformat(),
            schedule_type=data.schedule_type,
            total_hours_per_day=data.total_hours_per_day,
            total_hours_per_week=data.total_hours_per_week,
            daily_schedules=formatted_days,
            total_allocated_hours=round(total_allocated, 2)
        )
        
        self.schedules[schedule_id] = {
            "data": response.dict(),
            "daily_allocations": daily_schedules,
            "progress": {},
            "created_at": datetime.now()
        }
        
        return response
    
    def get_schedule(self, schedule_id: str) -> Optional[Dict]:
        return self.schedules.get(schedule_id)
    
    def update_progress(
        self, 
        schedule_id: str, 
        updates: List[Dict]
    ) -> Dict:
        if schedule_id not in self.schedules:
            return {"error": "Schedule not found. This can happen if the server instance restarted (ephemeral storage). Please regenerate your schedule."}
        
        for u in updates:
            self.schedules[schedule_id]["progress"][u["subject_id"]] = u["completed_hours"]
        
        return {"status": "progress updated", "schedule_id": schedule_id}
    
    def reschedule(self, schedule_id: str) -> Dict:
        from algorithms.dynamic_scheduler import DynamicScheduler
        
        if schedule_id not in self.schedules:
            return {"error": "Schedule not found (Session Expired). Please regenerate your schedule."}
        
        sched = self.schedules[schedule_id]
        dynamic = DynamicScheduler(sched["daily_allocations"])
        
        for subj_id, hours in sched["progress"].items():
            dynamic.progress_data[subj_id] = hours
        
        new_schedule = dynamic.reschedule(remaining_days=5)
        sched["daily_allocations"] = new_schedule
        
        return {"rescheduled": True, "new_schedule": new_schedule}
    
    def get_metrics(self, schedule_id: str) -> Dict:
        from algorithms.dynamic_scheduler import DynamicScheduler
        
        if schedule_id not in self.schedules:
            return {"error": "Schedule not found (Metrics Unavailable)."}
        
        sched = self.schedules[schedule_id]
        dynamic = DynamicScheduler(sched["daily_allocations"])
        
        for subj_id, hours in sched["progress"].items():
            dynamic.progress_data[subj_id] = hours
        
        return dynamic.get_efficiency_metrics(schedule_id)

schedule_service = ScheduleService()