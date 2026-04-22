// Identify system origin to set API context
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : ''; 

let currentSchedule = null;

// Utility: Get current date in YYYY-MM-DD format
function getTodayDate() {
    const today = new Date();
    const dd = String(today.getDate()).padStart(2, '0');
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const yyyy = today.getFullYear();
    return `${yyyy}-${mm}-${dd}`;
}

function addSubject() {
    const container = document.getElementById('subjectsList');
    const entry = document.createElement('div');
    entry.className = 'subject-entry';
    entry.innerHTML = `
        <input type="text" placeholder="SUBJECT IDENTITY" class="subject-name">
        <select class="subject-difficulty">
            <option value="1">Lvl 1 (Easy)</option>
            <option value="2">Lvl 2 (Medium)</option>
            <option value="3">Lvl 3 (Moderate)</option>
            <option value="4">Lvl 4 (Hard)</option>
            <option value="5" selected>Lvl 5 (Critical)</option>
        </select>
        <input type="date" class="subject-deadline" min="${getTodayDate()}">
        <button type="button" class="remove-subject" onclick="removeSubject(this)">X</button>
    `;
    container.appendChild(entry);
}


function removeSubject(button) {
    const entries = document.querySelectorAll('.subject-entry');
    if (entries.length > 1) {
        button.parentElement.remove();
    }
}

async function generateSchedule(event) {
    event.preventDefault();
    
    const totalHoursPerDay = parseFloat(document.getElementById('totalHoursDay').value);
    const totalHoursPerWeek = parseFloat(document.getElementById('totalHoursWeek').value);
    
    const subjects = [];
    document.querySelectorAll('.subject-entry').forEach(entry => {
        const name = entry.querySelector('.subject-name').value.trim();
        const difficulty = parseInt(entry.querySelector('.subject-difficulty').value);
        const deadline = entry.querySelector('.subject-deadline').value || null;
        
        if (name) {
            subjects.push({ name, difficulty, deadline });
        }
    });
    
    if (subjects.length === 0) {
        alert('ALERT: Target dataset empty. Please add at least one subject node.');
        return;
    }
    
    const requestData = {
        subjects,
        total_hours_per_day: totalHoursPerDay,
        total_hours_per_week: totalHoursPerWeek,
        schedule_type: 'weekly'
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/schedule/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error('Load distribution failed.');
        }
        
        currentSchedule = await response.json();
        displaySchedule(currentSchedule);
        
    } catch (error) {
        console.error('Core Logic Error:', error);
        alert('CRITICAL FAILURE: Could not connect to API. Verify backend infrastructure.');
    }
}

function displaySchedule(schedule) {
    document.getElementById('resultsSection').style.display = 'block';
    
    const totalHours = schedule.total_allocated_hours;
    
    document.getElementById('totalWeeklyHours').textContent = totalHours.toFixed(1) + 'H';
    document.getElementById('totalDailyHours').textContent = schedule.total_hours_per_day + 'H';
    document.getElementById('subjectCount').textContent = schedule.daily_schedules[0]?.allocations.length || 0;
    
    const dailyContainer = document.getElementById('dailySchedules');
    dailyContainer.innerHTML = '';
    
    const dayNames = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'];
    
    schedule.daily_schedules.forEach((day, index) => {
        const dayTotal = day.allocations.reduce((sum, a) => sum + a.allocated_hours, 0);
        
        let subjectsHtml = '';
        day.allocations.forEach(alloc => {
            const diffClass = alloc.difficulty >= 4 ? 'error' : (alloc.difficulty >= 3 ? 'warning' : '');
            
            subjectsHtml += `
                <div class="subject-item">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span class="subject-name" style="letter-spacing: 0.05em;">${alloc.subject_name.toUpperCase()}</span>
                        <span class="subject-hours">${alloc.allocated_hours}h</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div class="glow-point ${diffClass}"></div>
                        <span class="label-sm" style="font-size: 0.65rem;">LOAD LEVEL: ${alloc.difficulty}</span>
                    </div>
                </div>
            `;
        });
        
        const dayCard = document.createElement('div');
        dayCard.className = 'day-card';
        dayCard.innerHTML = `
            <div class="day-header">
                <span class="day-name">${dayNames[index] || 'NODE ' + (index + 1)}</span>
                <span class="label-sm">${dayTotal.toFixed(1)} HRS</span>
            </div>
            <div class="day-subjects">${subjectsHtml}</div>
        `;
        
        dailyContainer.appendChild(dayCard);
    });
    
    // Smooth scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

async function updateProgress() {
    if (!currentSchedule) return;
    
    const updates = [];
    document.querySelectorAll('.subject-entry').forEach((entry, index) => {
        const name = entry.querySelector('.subject-name').value;
        const completed = prompt(`UPDATE STATUS FOR ${name.toUpperCase()}:\nEnter completed cycle hours:`, '0');
        if (completed !== null) {
            updates.push({
                subject_id: `subj_${index}_${name.toLowerCase().replace(' ', '_')}`,
                completed_hours: parseFloat(completed) || 0
            });
        }
    });
    
    try {
        const response = await fetch(`${API_BASE}/api/schedule/${currentSchedule.id}/progress`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        
        if (response.ok) {
            loadMetrics();
        }
    } catch (error) {
        console.error('Status Sync Error:', error);
    }
}

async function reschedule() {
    if (!currentSchedule) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/schedule/${currentSchedule.id}/reschedule`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.new_schedule) {
                currentSchedule.daily_schedules = result.new_schedule;
                displaySchedule(currentSchedule);
            }
        }
    } catch (error) {
        console.error('Optimization Failure:', error);
    }
}

async function loadMetrics() {
    if (!currentSchedule) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/schedule/${currentSchedule.id}/metrics`);
        if (response.ok) {
            const metrics = await response.json();
            document.getElementById('fairnessIndex').textContent = metrics.fairness_index;
            document.getElementById('fairnessBar').style.width = (metrics.fairness_index * 100) + '%';
            
            document.getElementById('progressPercent').textContent = metrics.overall_progress_percent + '%';
            document.getElementById('progressBar').style.width = metrics.overall_progress_percent + '%';
        }
    } catch (error) {
        console.error('Metrics Retrieval Error:', error);
    }
}

document.getElementById('scheduleForm').addEventListener('submit', generateSchedule);

// Initialize system with contemporary temporal bounds
window.addEventListener('DOMContentLoaded', () => {
    const today = getTodayDate();
    document.querySelectorAll('.subject-deadline').forEach(el => {
        el.setAttribute('min', today);
    });
});