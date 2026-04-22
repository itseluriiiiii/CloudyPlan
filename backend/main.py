from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from uuid import uuid4
from algorithms.weighted_scheduler import generate_weekly_schedule
from algorithms.dynamic_scheduler import DynamicScheduler

app = Flask(__name__)
CORS(app)

schedules = {}

@app.route('/')
def root():
    return jsonify({
        "name": "Cloud-Based Smart Study Load Balancer",
        "version": "1.0.0",
        "status": "operational",
        "algorithms": {
            "weighted_load_balancing": "Proportional time allocation based on difficulty",
            "dynamic_scheduling": "Adaptive rescheduling with deadline priority"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/schedule/generate', methods=['POST'])
def create_schedule():
    data = request.get_json()
    
    schedule_id = f"sched_{uuid4().hex[:8]}"
    
    daily_schedules = generate_weekly_schedule(
        data['subjects'],
        data['total_hours_per_day'],
        data['total_hours_per_week']
    )
    
    total_allocated = sum(
        sum(a["allocated_hours"] for a in d["allocations"])
        for d in daily_schedules
    )
    
    response = {
        "id": schedule_id,
        "created_at": datetime.now().isoformat(),
        "schedule_type": data.get("schedule_type", "weekly"),
        "total_hours_per_day": data['total_hours_per_day'],
        "total_hours_per_week": data['total_hours_per_week'],
        "daily_schedules": daily_schedules,
        "total_allocated_hours": round(total_allocated, 2)
    }
    
    schedules[schedule_id] = {
        "data": response,
        "daily_allocations": daily_schedules,
        "progress": {},
        "created_at": datetime.now()
    }
    
    return jsonify(response), 201

@app.route('/api/schedule/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    if schedule_id not in schedules:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify(schedules[schedule_id]["data"])

@app.route('/api/schedule/<schedule_id>/progress', methods=['PUT'])
def update_progress(schedule_id):
    if schedule_id not in schedules:
        return jsonify({"error": "Schedule not found"}), 404
    
    updates = request.get_json()
    for upd in updates:
        schedules[schedule_id]["progress"][upd["subject_id"]] = upd["completed_hours"]
    
    return jsonify({"status": "progress updated", "schedule_id": schedule_id})

@app.route('/api/schedule/<schedule_id>/reschedule', methods=['POST'])
def reschedule(schedule_id):
    if schedule_id not in schedules:
        return jsonify({"error": "Schedule not found"}), 404
    
    sched = schedules[schedule_id]
    dynamic = DynamicScheduler(sched["daily_allocations"])
    
    for subj_id, hours in sched["progress"].items():
        dynamic.progress_data[subj_id] = hours
    
    new_schedule = dynamic.reschedule(remaining_days=5)
    sched["daily_allocations"] = new_schedule
    
    return jsonify({"rescheduled": True, "new_schedule": new_schedule})

@app.route('/api/schedule/<schedule_id>/metrics', methods=['GET'])
def get_metrics(schedule_id):
    if schedule_id not in schedules:
        return jsonify({"error": "Schedule not found"}), 404
    
    sched = schedules[schedule_id]
    dynamic = DynamicScheduler(sched["daily_allocations"])
    
    for subj_id, hours in sched["progress"].items():
        dynamic.progress_data[subj_id] = hours
    
    return jsonify(dynamic.get_efficiency_metrics(schedule_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)