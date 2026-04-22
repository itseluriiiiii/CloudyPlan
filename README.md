# 🌌 CloudyPlan | Cloud-Derived Study Load Balancer

[![System Status](https://img.shields.io/badge/System_Status-Optimized-00ffcc?style=for-the-badge&logo=statuspage)](https://cloudy-plan.vercel.app)
[![Tech Stack](https://img.shields.io/badge/Stack-Flask_%7C_Vanilla_JS-blueviolet?style=for-the-badge)](https://github.com/arnaveluri/CloudyPlan)

**CloudyPlan** is a specialized study optimization engine that applies cloud infrastructure load-balancing principles to academic workload management. By implementing weighted distribution algorithms and Jain’s Fairness Index, it ensures peak intellectual throughput and eliminates focus-starvation across disparate study nodes.

---

## 🚀 Key Features

- **Weighted Load Balancing**: Proportional time allocation based on subject difficulty (Lvl 1-5).
- **Dynamic Rescheduling**: Adaptive scheduler that re-optimizes remaining slots based on progress and deadlines.
- **Jain’s Fairness Index**: Real-time metric calculation to ensure balanced distribution of effort.
- **Observatory UI**: A high-contrast, data-driven "Neon Monolith" aesthetic designed for focus.
- **Node Monitoring**: Track progress across individual "Target Analytes" (Subjects).

## 🛠️ Tech Stack

### Frontend (User Interface)
- **HTML5 & Vanilla CSS**: Custom-built design system with a technical "Observatory" aesthetic.
- **Vanilla JavaScript**: Reactive UI updates and client-side distribution logic.
- **Design Principles**: Glassmorphism, pulse indicators, and responsive grid layouts.

### Backend (Algorithmic Engine)
- **Python / Flask**: Restful API for schedule generation and metric calculation.
- **Weighted Distribution Algorithm**: Ensures higher-difficulty subjects receive statistically appropriate bandwidth.
- **Dynamic Scheduler**: Handles adaptive rescheduling using Python-based optimization logic.

---

## 📂 Project Structure

```text
Cloud_Computing/
├── frontend/           # UI Components and Design System
│   ├── css/            # "Neon Monolith" Stylesheets
│   ├── js/             # UI Logic and Client-side API calls
│   └── index.html      # Main Dashboard View
├── backend/            # Core Algorithmic Engine
│   ├── algorithms/     # Weighted & Dynamic Scheduling logic
│   ├── routes/         # Flask API Endpoints
│   └── main.py         # Application Entry Point
├── cloudsim/           # Simulation environment for testing
├── docs/               # Documentation and Architectural Diagrams
└── vercel.json         # Deployment configuration
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- Modern Web Browser (Chrome/Firefox/Edge)

### 1. Clone & Setup Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
*The backend will boot up on `http://localhost:8000`.*

### 2. Launch Frontend
Simply open `frontend/index.html` in your browser or use a Live Server.

---

## 🧬 Algorithm Deep Dive

### 1. Weighted Round-Robin
The system calculates the `total_weight` of all subjects (Analyte Weights) and distributes the `daily_quota` proportionally.
$$Weight_i = \frac{Difficulty_i}{\sum Difficulty}$$

### 2. Jain's Fairness Index
Used to determine if the workload is being distributed equitably among subjects.
$$J(x) = \frac{(\sum_{i=1}^n x_i)^2}{n \sum_{i=1}^n x_i^2}$$

---

## 👥 Development Team
- **Arnav Eluri**
- **Abhilash KM**
- **Akshay Kumar M**
- **Anish Shetty**

---

<p align="center">
  <i>System Status: Operational | Peak Efficiency | Optimized for Throughput</i><br>
  Built for the Cloud Computing Laboratory.
</p>
