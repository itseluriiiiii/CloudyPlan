from flask import Flask, jsonify, request
from flask_cors import CORS
from services.schedule_service import schedule_service
from models.schemas import ScheduleCreate

app = Flask(__name__)
# Enable CORS for all routes to allow local development (Live Server, etc.)
CORS(app)

@app.route('/')
def root():
    return jsonify({
        "name": "CloudyPlan API",
        "version": "1.1.0",
        "status": "operational",
        "features": ["Weighted Load Balancing", "Dynamic Rescheduling", "Fairness Metrics"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/schedule/generate', methods=['POST'])
def create_schedule():
    data = request.get_json()
    
    try:
        # Validate and create schedule
        schedule_data = ScheduleCreate(
            subjects=data.get('subjects', []),
            total_hours_per_day=float(data.get('total_hours_per_day', 4)),
            total_hours_per_week=float(data.get('total_hours_per_week', 28)),
            schedule_type=data.get('schedule_type', 'weekly')
        )
        
        response = schedule_service.create_schedule(schedule_data)
        return jsonify(response.dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/schedule/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    sched = schedule_service.get_schedule(schedule_id)
    if not sched:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify(sched["data"])

@app.route('/api/schedule/<schedule_id>/progress', methods=['PUT'])
def update_progress(schedule_id):
    updates = request.get_json()
    result = schedule_service.update_progress(schedule_id, updates)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)

@app.route('/api/schedule/<schedule_id>/reschedule', methods=['POST'])
def reschedule(schedule_id):
    # For now, hardcoded 5 days, but could be dynamic
    result = schedule_service.reschedule(schedule_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)

@app.route('/api/schedule/<schedule_id>/metrics', methods=['GET'])
def get_metrics(schedule_id):
    result = schedule_service.get_metrics(schedule_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)

if __name__ == '__main__':
    # When running locally, use port 8000
    app.run(host='0.0.0.0', port=8000, debug=True)