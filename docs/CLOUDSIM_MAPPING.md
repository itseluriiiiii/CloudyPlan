# CloudSim Integration Documentation

This document explains how the Smart Study Load Balancer uses CloudSim for simulation and validation.

---

## Overview

CloudSim is used as a **research and validation layer** to:
1. Simulate scheduling efficiency under various workloads
2. Validate algorithm performance metrics
3. Test edge cases (high load, tight deadlines)

**Note**: CloudSim is NOT used in production. It's a simulation-only layer.

---

## Entity Mapping

### Study Concepts to CloudSim Entities

| Study Concept | CloudSim Entity | Description |
|---------------|----------------|-------------|
| Study Hours | Cloudlet Length (MI) | Total computational work |
| Subject | Virtual Machine (VM) | Dedicated resource for each subject |
| Difficulty | MIPS Rating | Processing capacity |
| Study Session | Cloudlet | Individual study task |
| Deadline | Cloudlet Deadline | Time constraint |
| Schedule | Submit to Broker | Task distribution |
| Progress | Cloudlet Completion % | Execution status |

### Parameter Mapping

```
Study Difficulty (1-5) → MIPS (250-1250)
  - Easy (1) → 250 MIPS
  - Medium (2) → 500 MIPS
  - Moderate (3) → 750 MIPS
  - Hard (4) → 1000 MIPS
  - Very Hard (5) → 1250 MIPS

Study Hours → Cloudlet Length (MI)
  - 1 hour → 1000 MI
  - 2 hours → 2000 MI
  - etc.
```

---

## CloudSim Simulation Code

### Java Implementation

**Location**: `cloudsim/src/main/java/edu/cloudcomputing/StudyLoadBalancerSimulation.java`

```java
public class StudyLoadBalancerSimulation {
    
    // Step 1: Create VMs from subjects
    private List<Vm> createSubjectVMs(int numSubjects) {
        List<Vm> vms = new ArrayList<>();
        
        String[] subjects = {"Mathematics", "Physics", "Chemistry", "Biology", "English"};
        int[] difficulties = {5, 4, 3, 4, 2};
        
        for (int i = 0; i < numSubjects; i++) {
            // Higher difficulty = more MIPS capacity
            int mips = difficulties[i] * 250;
            Vm vm = new Vm(i, broker.getId(), mips, difficulties[i], 
                          ram, bw, size, "Xen", scheduler);
            vms.add(vm);
        }
        return vms;
    }
    
    // Step 2: Create Cloudlets from study sessions
    private List<Cloudlet> createStudyCloudlets() {
        // Length tied to difficulty
        long[] sessionLengths = {5000, 4000, 3000, 4000, 2000};
        ...
    }
}
```

---

## Simulation Metrics

### 1. Completion Time

**Definition**: Total time to complete all study sessions (cloudlets)

**Calculation**:
```
Completion_Time = max(all_cloudlets.finishTime)
```

**Target**: Lower is better

---

### 2. Fairness Index (Jain's)

**Definition**: Measures how evenly resources are distributed

**Formula**:
```
FI = (Σx_i)² / (n × Σx_i²)

Where:
- x_i = completion ratio for subject i
- n = number of subjects
```

**Interpretation**:
| Value | Meaning |
|-------|---------|
| 1.0 | Perfect fairness |
| > 0.8 | Good fairness |
| 0.5-0.8 | Moderate imbalance |
| < 0.5 | Significant unfairness |

---

### 3. Resource Utilization

**Definition**: Percentage of total available time used

**Formula**:
```
Utilization = (sum_completion_time / total_available_time) × 100
```

**Target**: 70-90% (leaves buffer for breaks)

---

### 4. Deadline Miss Rate

**Definition**: Percentage of subjects missing deadline

**Formula**:
```
Miss_Rate = (missed_deadlines / total_subjects) × 100
```

---

## Running the Simulation

### Prerequisites

1. Install Java 11+
2. Install Maven
3. CloudSim dependency (included in pom.xml)

### Commands

```bash
# Navigate to cloudsim directory
cd cloudsim

# Compile
mvn compile

# Run simulation
mvn exec:java

# Output:
# === Cloud-Based Study Load Balancer Simulation ===
# Avg Completion Time: 12.45 time units
# Fairness Index (Jain): 0.923
# Resource Utilization: 78.3%
# Task Success Rate: 100.0%
```

---

## Edge Case Testing

### Test 1: High Difficulty Variance
```
Subjects: Math(5), English(1)
Expected: Math gets 5x more time
```

### Test 2: Tight Deadlines
```
All subjects due in 2 days
Expected: Even distribution
```

### Test 3: Burnout Prevention
```
8 subjects, 20 hours/day
Expected: Max 4h per subject
```

### Test 4: Empty Schedule
```
0 subjects
Expected: Error handling
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Production                             │
│  ┌─────────────┐    ┌─────────────────────────┐    │
│  │   Frontend │───▶│   FastAPI Backend      │    │
│  │   (HTML)   │    │   - weighted_scheduler│    │
│  │            │    │   - dynamic_scheduler │    │
│  └─────────────┘    └─────────────────────────┘    │
│                            │                      │
└────────────────────────────┼──────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  Simulation     │
                    │  (CloudSim)     │
                    │  - validation   │
                    │  - testing     │
                    └─────────────────┘
```

---

## Benefits of CloudSim Integration

1. **Algorithm Validation**: Test weighted load balancing under various conditions
2. **Performance Metrics**: Get real fairness index, utilization stats
3. **Research**: Publish simulation results for academic purposes
4. **Edge Cases**: Test extreme scenarios safely

---

## Limitations

1. **Not for Production**: Simulation only
2. **Java Dependency**: Requires JVM
3. **Conceptual Mapping**: May not perfectly map to real-world study behavior
4. **No User Feedback**: Simulates only, doesn't adapt to real user data

---

## Future Enhancements

1. Machine learning for adaptive difficulty estimation
2. Historical data analysis for better predictions
3. Integration with calendar apps (Google Calendar, etc.)
4. Mobile companion app