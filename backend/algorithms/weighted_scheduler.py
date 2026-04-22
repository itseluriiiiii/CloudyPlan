from typing import List, Dict, Any
from dataclasses import dataclass
from typing import Optional

class WeightedLoadBalancer:
    MIN_HOURS_PER_SUBJECT = 0.5
    MAX_HOURS_PER_DAY = 4.0
    
    def __init__(self, subjects: List[Dict[str, Any]], total_hours: float):
        self.subjects = subjects
        self.total_hours = total_hours
        self.total_difficulty = sum(s.get('difficulty', 1) for s in subjects)
    
    def calculate_weight(self, difficulty: int) -> float:
        if self.total_difficulty == 0:
            return 1.0 / len(self.subjects) if self.subjects else 1.0
        return difficulty / self.total_difficulty
    
    def allocate_hours(self, weight: float) -> float:
        hours = weight * self.total_hours
        hours = max(self.MIN_HOURS_PER_SUBJECT, min(hours, self.MAX_HOURS_PER_DAY))
        return round(hours * 2) / 2
    
    def generate_allocations(self) -> List[Dict[str, Any]]:
        allocations = []
        
        for idx, subject in enumerate(self.subjects):
            difficulty = subject.get('difficulty', 1)
            weight = self.calculate_weight(difficulty)
            hours = self.allocate_hours(weight)
            
            allocations.append({
                "subject_id": f"subj_{idx}_{subject.get('name', 'unknown').lower().replace(' ', '_')}",
                "subject_name": subject.get('name', f'Subject {idx}'),
                "difficulty": difficulty,
                "allocated_hours": hours,
                "weight": round(weight, 3),
                "deadline": subject.get('deadline')
            })
        
        return self._normalize_allocations(allocations)
    
    def _normalize_allocations(self, allocations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        total_allocated = sum(a.get('allocated_hours', 0) for a in allocations)
        diff = self.total_hours - total_allocated
        
        if abs(diff) < 0.01 or not allocations:
            return allocations
        
        idx = len(allocations) - 1
        current = allocations[idx].get('allocated_hours', 0)
        new_hours = max(self.MIN_HOURS_PER_SUBJECT, current + diff)
        allocations[idx]['allocated_hours'] = new_hours
        
        return allocations

def generate_weekly_schedule(subjects: List[Dict[str, Any]], hours_per_day: float, hours_per_week: float) -> List[Dict[str, Any]]:
    daily_allocations = []
    
    for day in range(1, 8):
        balancer = WeightedLoadBalancer(subjects, hours_per_day)
        day_allocations = balancer.generate_allocations()
        
        daily_entry = {
            "day": day,
            "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day - 1],
            "allocations": day_allocations
        }
        daily_allocations.append(daily_entry)
    
    return daily_allocations