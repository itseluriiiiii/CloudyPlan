# Sample Inputs and Outputs

This document provides example API requests and responses for the Smart Study Load Balancer.

---

## 1. Generate Schedule (POST /api/schedule/generate)

### Sample Request

```json
{
    "subjects": [
        {
            "name": "Mathematics",
            "difficulty": 5,
            "deadline": "2026-05-15"
        },
        {
            "name": "Physics",
            "difficulty": 4,
            "deadline": "2026-05-20"
        },
        {
            "name": "Computer Science",
            "difficulty": 3,
            "deadline": "2026-05-10"
        },
        {
            "name": "English",
            "difficulty": 2,
            "deadline": "2026-05-25"
        }
    ],
    "total_hours_per_day": 4.0,
    "total_hours_per_week": 20.0,
    "schedule_type": "weekly"
}
```

### Sample Response

```json
{
    "id": "sched_a1b2c3d4",
    "created_at": "2026-04-21T10:30:00Z",
    "schedule_type": "weekly",
    "total_hours_per_day": 4.0,
    "total_hours_per_week": 20.0,
    "daily_schedules": [
        {
            "day": 1,
            "allocations": [
                {
                    "subject_id": "subj_0_mathematics",
                    "subject_name": "Mathematics",
                    "difficulty": 5,
                    "allocated_hours": 1.5,
                    "weight": 0.357,
                    "deadline": "2026-05-15"
                },
                {
                    "subject_id": "subj_1_physics",
                    "subject_name": "Physics",
                    "difficulty": 4,
                    "allocated_hours": 1.0,
                    "weight": 0.286,
                    "deadline": "2026-05-20"
                },
                {
                    "subject_id": "subj_2_computer_science",
                    "subject_name": "Computer Science",
                    "difficulty": 3,
                    "allocated_hours": 1.0,
                    "weight": 0.214,
                    "deadline": "2026-05-10"
                },
                {
                    "subject_id": "subj_3_english",
                    "subject_name": "English",
                    "difficulty": 2,
                    "allocated_hours": 0.5,
                    "weight": 0.143,
                    "deadline": "2026-05-25"
                }
            ]
        },
        {
            "day": 2,
            "allocations": [...]
        },
        ...
    ],
    "total_allocated_hours": 20.0
}
```

---

## 2. Get Schedule (GET /api/schedule/{id})

### Request
```
GET /api/schedule/sched_a1b2c3d4
```

### Response
```json
{
    "id": "sched_a1b2c3d4",
    "created_at": "2026-04-21T10:30:00Z",
    "schedule_type": "weekly",
    "total_hours_per_day": 4.0,
    "total_hours_per_week": 20.0,
    "daily_schedules": [...],
    "total_allocated_hours": 20.0
}
```

---

## 3. Update Progress (PUT /api/schedule/{id}/progress)

### Request
```json
[
    {
        "subject_id": "subj_0_mathematics",
        "completed_hours": 1.5
    },
    {
        "subject_id": "subj_1_physics",
        "completed_hours": 0.5
    },
    {
        "subject_id": "subj_2_computer_science",
        "completed_hours": 1.0
    },
    {
        "subject_id": "subj_3_english",
        "completed_hours": 0.0
    }
]
```

### Response
```json
{
    "status": "progress updated",
    "schedule_id": "sched_a1b2c3d4"
}
```

---

## 4. Get Metrics (GET /api/schedule/{id}/metrics)

### Request
```
GET /api/schedule/sched_a1b2c3d4/metrics
```

### Response
```json
{
    "schedule_id": "sched_a1b2c3d4",
    "total_planned_hours": 20.0,
    "total_completed_hours": 3.0,
    "overall_progress_percent": 15.0,
    "fairness_index": 0.892,
    "subject_progress": [
        {
            "subject_id": "subj_0_mathematics",
            "subject_name": "Mathematics",
            "planned_hours": 7.5,
            "completed_hours": 1.5,
            "remaining_hours": 6.0,
            "progress_percent": 20.0
        },
        {
            "subject_id": "subj_1_physics",
            "subject_name": "Physics",
            "planned_hours": 5.5,
            "completed_hours": 0.5,
            "remaining_hours": 5.0,
            "progress_percent": 9.1
        },
        {
            "subject_id": "subj_2_computer_science",
            "subject_name": "Computer Science",
            "planned_hours": 4.5,
            "completed_hours": 1.0,
            "remaining_hours": 3.5,
            "progress_percent": 22.2
        },
        {
            "subject_id": "subj_3_english",
            "subject_name": "English",
            "planned_hours": 2.5,
            "completed_hours": 0.0,
            "remaining_hours": 2.5,
            "progress_percent": 0.0
        }
    ]
}
```

---

## 5. Reschedule (POST /api/schedule/{id}/reschedule)

### Request
```json
{
    "reason": "fell behind by 2 days"
}
```

### Response
```json
{
    "rescheduled": true,
    "new_schedule": [
        {
            "day": 1,
            "day_name": "Tuesday",
            "allocations": [
                {
                    "subject_id": "subj_2_computer_science",
                    "subject_name": "Computer Science",
                    "allocated_hours": 2.0,
                    "difficulty": 3,
                    "weight": 0.333,
                    "is_priority": true
                },
                {
                    "subject_id": "subj_0_mathematics",
                    "subject_name": "Mathematics",
                    "allocated_hours": 1.5,
                    "difficulty": 5,
                    "weight": 0.25,
                    "is_priority": true
                },
                ...
            ]
        },
        ...
    ]
}
```

---

## Example Calculation

### Input
- 4 subjects (Math:5, Physics:4, CS:3, English:2)
- 20 hours/week, 4 hours/day
- Total difficulty = 14

### Weighted Allocation
| Subject | Difficulty | Weight | Raw Hours | Rounded Hours |
|---------|------------|--------|----------|---------------|
| Math | 5 | 0.357 | 7.14 | 7.0 |
| Physics | 4 | 0.286 | 5.71 | 5.5 |
| CS | 3 | 0.214 | 4.29 | 4.5 |
| English | 2 | 0.143 | 2.86 | 3.0 |
| **Total** | 14 | 1.0 | 20.0 | 20.0 |

### Daily Breakdown
```
Day 1: Math(1.5) + Physics(1.0) + CS(1.0) + English(0.5) = 4.0h
Day 2: Math(1.5) + Physics(1.0) + CS(1.0) + English(0.5) = 4.0h
Day 3: Math(1.5) + Physics(1.0) + CS(1.0) + English(0.5) = 4.0h
Day 4: Math(1.0) + Physics(1.0) + CS(1.0) + English(0.5) = 3.5h
Day 5: Math(1.5) + Physics(1.5) + CS(0.5) + English(0.5) = 4.0h
...
```