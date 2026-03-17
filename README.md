# 🤖 AI Automated Home Service Robot

An intelligent, autonomous home service robot simulation powered by advanced Artificial Intelligence techniques. This project demonstrates house-scale navigation, task scheduling, and state-based reasoning to perform domestic chores like cleaning, serving items, and self-recharging.

---

## 🌟 Key Features

- **💻 Enterprise-Grade GUI**: A modern, dark-themed dashboard built with Tkinter for real-time simulation monitoring.
- **🧭 Multi-Algorithm Pathfinding**: Supports **A***, **BFS**, **DFS**, **UCS**, and **Greedy BFS** for optimal navigation.
- **🗓️ Intelligent Task Scheduling**: Uses **Constraint Satisfaction Problems (CSP)** to prioritize and sequence chores (e.g., Charge before Serving).
- **🧠 Knowledge-Based Reasoning**: Implements propositional logic with **Forward Chaining** for autonomous decision-making (e.g., detecting low battery).
- **🏗️ Hierarchical Planning**: Decomposes high-level goals (e.g., "Serve Tea") into actionable subtasks using **HTN-like decomposition**.
- **🚧 Dynamic Environment**: Interactive grid where users can add obstacles in real-time.

---

## 🛠️ Technology Stack

- **Language**: Python 3.x
- **GUI Framework**: Tkinter (with custom dark-themed styling)
- **AI Paradigms**:
  - Pathfinding & Search
  - Constraint Satisfaction Problems (CSP)
  - Knowledge Representation & Reasoning
  - Hierarchical Task Planning (HTN)

---

## 📁 Project Structure

```text
├── Project Code/
│   ├── gui.py              # Main Graphic User Interface & Controller
│   ├── main.py             # CLI Entry point & Core logic demo
│   ├── robot.py            # Robot state & basic movement logic
│   ├── environment.py      # Grid world representation & obstacles
│   ├── search.py           # A*, BFS, DFS, UCS implementations
│   ├── csp.py              # Constraint Satisfaction Problem solver
│   ├── planner.py          # Hierarchical task planner
│   └── knowledge_base.py   # Propositional logic & Forward Chaining
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ installed on your system.

### Running the GUI Simulation
To experience the full interactive simulation, run the `gui.py` file:
```bash
python "Project Code/gui.py"
```

### Running the CLI Demo
To see a console-based demonstration of the AI logic:
```bash
python "Project Code/main.py"
```

---

## 🤖 AI Modules Overview

### 1. Navigation & Search (`search.py`)
The robot calculates paths using various search algorithms. **A*** is used by default for its efficiency in finding the shortest path using Manhattan distance heuristics.

### 2. Task Scheduling (`csp.py`)
When multiple tasks are assigned, the **CSP Solver** ensures they are executed in a logical order (e.g., "Recharge" must happen before "Serve Tea" if the battery is low), respecting time and resource constraints.

### 3. Reasoning & Knowledge (`knowledge_base.py`)
The robot maintains a Knowledge Base. When facts like `BatteryLow` are added, the **Forward Chaining** engine automatically derives the need to `ShouldCharge`.

### 4. Hierarchical Planning (`planner.py`)
Complex goals like "Deliver Tea to LivingRoom" are decomposed into subtasks:
1. `navigate(Kitchen)`
2. `pick(TeaCup)`
3. `navigate(LivingRoom)`
4. `drop(TeaCup)`

---

## 🤝 Contributors

*   **Muhammad Huzaifa** - Lead Contributor & AI Developer

---

*Developed for the 4th Semester Artificial Intelligence Project.*
