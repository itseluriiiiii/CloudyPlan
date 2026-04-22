from typing import List, Dict, Any, Optional
from datetime import datetime, date

class DynamicScheduler:
    def __init__(self, current_allocations: List[Dict[str, Any]], days_elapsed: int = 0):
        self.current_allocations = current_allocations
        self.days_elapsed = days_elapsed
        self.progress_data: Dict[str, float] = {}
    
    def update_progress(self, subject_id: str, completed_hours: float) -> Dict[str, Any]:
        self.progress_data[subject_id] = completed_hours
        return self.get_progress_summary()
    
    def get_progress_summary(self) -> Dict[str, Any]:
        summary = []
        
        for day_data in self.current_allocations:
            for alloc in day_data.get("allocations", []):
                subj_id = alloc.get("subject_id", "")
                planned = alloc.get("allocated_hours", 0)
                completed = self.progress_data.get(subj_id, 0)
                remaining = max(0, planned - completed)
                
                summary.append({
                    "subject_id": subj_id,
                    "subject_name": alloc.get("subject_name", ""),
                    "planned_hours": planned,
                    "completed_hours": completed,
                    "remaining_hours": remaining,
                    "progress_percent": round((completed / planned * 100) if planned > 0 else 0, 1)
                })
        
        return {"subjects": summary}
    
    def reschedule(self, new_deadlines: Optional[Dict[str, str]] = None, remaining_days: int = 7) -> List[Dict[str, Any]]:
        progress = self.get_progress_summary()
        subjects = progress.get("subjects", [])
        
        if not subjects:
            return self.current_allocations
        
        total_remaining = sum(s.get("remaining_hours", 0) for s in subjects)
        
        if total_remaining <= 0:
            return self.current_allocations
        
        priority_scores = []
        
        for subj in subjects:
            score = 0
            subj_id = subj.get("subject_id", "")
            
            if new_deadlines and subj_id in new_deadlines:
                try:
                    days_until = (date.fromisoformat(new_deadlines[subj_id]) - date.today()).days
                    if days_until > 0:
                        score += (30 - days_until) * 2
                except:
                    pass
            
            score += subj.get("remaining_hours", 0) * 3
            
            if subj.get("progress_percent", 0) < 50:
                score += 10
            
            priority_scores.append((subj_id, score, subj))
        
        priority_scores.sort(key=lambda x: x[1], reverse=True)
        
        new_allocations = []
        hours_per_day = total_remaining / max(remaining_days, 1)
        
        for day in range(1, remaining_days + 1):
            day_hours = min(hours_per_day, total_remaining / (remaining_days - day + 1))
            remaining_for_day = day_hours
            
            day_schedule = {
                "day": day,
                "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][(day - 1) % 7],
                "allocations": []
            }
            
            for subj_id, _, subj_data in priority_scores:
                if remaining_for_day <= 0:
                    break
                
                hours_to_alloc = min(subj_data.get("remaining_hours", 0), remaining_for_day)
                
                if hours_to_alloc > 0:
                    day_schedule["allocations"].append({
                        "subject_id": subj_id,
                        "subject_name": subj_data.get("subject_name", ""),
                        "allocated_hours": round(hours_to_alloc, 2),
                        "difficulty": 3,
                        "weight": round(hours_to_alloc / day_hours, 3) if day_hours > 0 else 0,
                        "is_priority": True
                    })
                    
                    remaining_for_day -= hours_to_alloc
            
            new_allocations.append(day_schedule)
            total_remaining -= day_hours
        
        return new_allocations
    
    def calculate_fairness_index(self) -> float:
        progress = self.get_progress_summary()
        subjects = progress.get("subjects", [])
        
        if not subjects:
            return 1.0
        
        completed = [s.get("completed_hours", 0) for s in subjects]
        
        if sum(completed) == 0:
            return 1.0
        
        n = len(completed)
        sum_completed = sum(completed)
        sum_squares = sum(c * c for c in completed)
        
        if sum_squares == 0:
            return 1.0
        
        fairness = (sum_completed * sum_completed) / (n * sum_squares)
        return round(fairness, 3)
    
    def get_efficiency_metrics(self, schedule_id: str) -> Dict[str, Any]:
        progress = self.get_progress_summary()
        subjects = progress.get("subjects", [])
        
        total_planned = sum(s.get("planned_hours", 0) for s in subjects)
        total_completed = sum(s.get("completed_hours", 0) for s in subjects)
        
        progress_percent = (total_completed / total_planned * 100) if total_planned > 0 else 0
        
        return {
            "schedule_id": schedule_id,
            "total_planned_hours": round(total_planned, 2),
            "total_completed_hours": round(total_completed, 2),
            "overall_progress_percent": round(progress_percent, 1),
            "fairness_index": self.calculate_fairness_index(),
            "subject_progress": subjects
        }