# Smart Study Load Balancer - Algorithms Documentation

This document explains the core algorithms behind the Cloud-Based Smart Study Load Balancer.

---

## 1. Weighted Load Balancing Algorithm

### Purpose
Distributes study hours proportionally based on subject difficulty to ensure fair allocation while prioritizing harder subjects.

### Formula
```
Weight_i = Difficulty_i / Σ(Difficulties)
Hours_i = Weight_i × Total_Hours_Available
```

### Implementation Details

**Location**: `backend/algorithms/weighted_scheduler.py`

```python
class WeightedLoadBalancer:
    MIN_HOURS_PER_SUBJECT = 0.5
    MAX_HOURS_PER_DAY = 4.0
    
    def calculate_weight(self, difficulty: int) -> float:
        if self.total_difficulty == 0:
            return 1.0 / len(self.subjects)
        return difficulty / self.total_difficulty
    
    def allocate_hours(self, weight: float) -> float:
        hours = weight * self.total_hours
        hours = max(self.MIN_HOURS_PER_SUBJECT, min(hours, self.MAX_HOURS_PER_DAY))
        return round(hours * 2) / 2  # Round to nearest 0.5
```

### Constraints
- **Minimum**: 0.5 hours per subject (prevents neglect)
- **Maximum**: 4 hours per subject per day (prevents burnout)
- **Rounding**: Allocated hours rounded to nearest 0.5 hour

### Example
```
Subjects: Math(5), Physics(4), CS(3), English(2)
Total Hours: 20 hours

Weights:
- Math: 5/14 = 0.357 → 7.14h
- Physics: 4/14 = 0.286 → 5.71h
- CS: 3/14 = 0.214 → 4.29h
- English: 2/14 = 0.143 → 2.86h

Total: 20h (normalized)
```

---

## 2. Dynamic Scheduling Algorithm

### Purpose
Adaptively reschedules study time when the user falls behind, prioritizing subjects with upcoming deadlines and lower completion rates.

### Features

**Location**: `backend/algorithms/dynamic_scheduler.py`

1. **Progress Tracking**
   - Tracks completed vs planned hours per subject
   - Calculates remaining hours
   - Computes progress percentage

2. **Deficit Detection**
   - Triggers when completed_hours < expected_hours
   - Based on days elapsed vs schedule timeline

3. **Rescheduling Logic**
   - Redistributes remaining hours across remaining days
   - Prioritizes by deadline proximity
   - Boosts priority for subjects with <50% progress

### Priority Score Formula
```
Priority_Score = Deadline_Score + Remaining_Hours_Score + Lag_Score

Where:
- Deadline_Score = (30 - days_until_deadline) × 2 (if deadline exists)
- Remaining_Hours_Score = remaining_hours × 3
- Lag_Score = +10 if progress_percent < 50%
```

### Implementation

```python
def reschedule(self, new_deadlines=None, remaining_days=7):
    priority_scores = []
    
    for subj in subjects:
        score = 0
        
        # Deadline priority
        if new_deadlines and subj["subject_id"] in new_deadlines:
            days_until = (deadline - today).days
            if days_until > 0:
                score += (30 - days_until) * 2
        
        # Remaining hours priority
        score += subj["remaining_hours"] * 3
        
        # Lag priority (if behind)
        if subj["progress_percent"] < 50:
            score += 10
        
        priority_scores.append((subj["subject_id"], score))
    
    # Sort by priority (highest first)
    priority_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Redistribute hours
    ...
```

---

## 3. Fairness Index (Jain's)

### Purpose
Measures how evenly study time is distributed across subjects.

### Formula
```
Fairness_Index = (Σx_i)² / (n × Σx_i²)

Where:
- x_i = hours completed for subject i
- n = number of subjects
```

### Interpretation
| Value | Interpretation |
|-------|----------------|
| 1.0 | Perfectly fair |
| 0.8 - 0.99 | Fair |
| 0.5 - 0.79 | Moderate imbalance |
| < 0.5 | Significant imbalance |

---

## 4. CloudSim Entity Mapping

| Study Concept | CloudSim Entity | Parameters |
|---------------|-----------------|------------|
| Study Hours | Cloudlet Length (MI) | 1000 per difficulty |
| Subject | Virtual Machine | 1 VM per subject |
| Difficulty | MIPS | difficulty × 250 |
| Study Session | Cloudlet | Individual task |
| Deadline | Cloudlet Deadline | Custom attribute |
| Schedule | Broker | DatacenterBroker |

### Simulation Metrics

1. **Completion Time**: Total time to complete all cloudlets
2. **Fairness Index**: Jain's index for task distribution
3. **Resource Utilization**: (Active time / Total time) × 100
4. **Success Rate**: Completed cloudlets / Total cloudlets

---

## Algorithm Flow Summary

```
User Input → Weighted Load Balancer → Initial Schedule
                                          ↓
                              Dynamic Scheduler (monitoring)
                                          ↓
                    ┌─────────────────────┴─────────────────────┐
                    ↓                                           ↓
            On Track                                    Behind Schedule
                    ↓                                           ↓
            Continue                               Reschedule with priority
                    ↓                                           ↓
            Normal Execution                          Boost deadline subjects
                                          ↓
                                    Redistribute remaining hours
```