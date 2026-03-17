import tkinter as tk
from tkinter import ttk, font, messagebox
import threading
import time
from environment import Environment
from robot import Robot
from knowledge_base import KnowledgeBase
from csp import CSP, all_different_time_constraint, precedence_constraint
from planner import HierarchicalPlanner
from search import a_star_search, bfs_search, dfs_search, ucs_search, greedy_bfs_search

# --- COLOR PALETTE (PRO DARK THEME) ---
# Modern, high-contrast, professional look
COLOR_BG_DARK = "#121212"       # Deepest Black
COLOR_BG_PANEL = "#1E1E1E"      # Panel Background
COLOR_BG_CARD = "#252526"       # Card Background
COLOR_FG_PRIMARY = "#E0E0E0"    # Primary Text
COLOR_FG_SECONDARY = "#A0A0A0"  # Secondary Text
COLOR_ACCENT = "#007ACC"        # VS Code Blue / Professional Blue
COLOR_ACCENT_HOVER = "#0098FF"  
COLOR_SUCCESS = "#4EC9B0"       # Soft Green
COLOR_WARNING = "#CE9178"       # Soft Orange/Red
COLOR_ERROR = "#F44747"         # Soft Red
COLOR_GRID_WALL = "#3C3C3C"     # Wall Color
COLOR_GRID_EMPTY = "#1E1E1E"    # Grid Background
COLOR_GRID_LINE = "#2D2D2D"     # Grid Lines

class GUIPlanner(HierarchicalPlanner):
    """
    Extensions of HierarchicalPlanner to support GUI updates.
    """
    def __init__(self, robot, environment, gui):
        super().__init__(robot, environment)
        self.gui = gui

    def execute_subtask(self, task, search_algorithm=a_star_search):
        action = task[0]
        
        if action == 'navigate':
            target_name = task[1]
            target_pos = self.environment.locations.get(target_name)
            
            if not target_pos:
                self.gui.log(f"Planner: Unknown location {target_name}", "error")
                return False
                
            self.gui.log(f"Planner: Navigating to {target_name}...", "info")
            self.gui.update_status(f"Moving to {target_name}...")
            
            path = search_algorithm(self.environment, self.robot.position, target_pos)
            
            if not path:
                self.gui.log("Planner: No path found!", "error")
                return False
                
            # Draw Path
            self.gui.draw_path_overlay(path)
            
            # Execute path movement
            for next_pos in path:
                if next_pos == self.robot.position: continue
                
                if self.robot.move(next_pos):
                    self.gui.update_grid() # Thread-safe redraw
                    self.gui.update_battery_label()
                    time.sleep(0.2) # Smooth animation
                else:
                    self.gui.log("Planner: Movement blocked!", "error")
                    return False
            return True
            
        elif action == 'pick':
            item = task[1]
            self.robot.pick_item(item)
            self.gui.log(f"Robot: Picked up {item}", "success")
            self.gui.update_grid()
            time.sleep(0.3)
            return True
            
        elif action == 'drop':
            self.robot.drop_item()
            self.gui.log("Robot: Dropped item", "success")
            self.gui.update_grid()
            time.sleep(0.3)
            return True
            
        return False

class HomeServiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Service Robot - Enterprise Edition")
        # Start maximized or fallback to large size
        try:
            self.root.state('zoomed')
        except:
            self.root.geometry("1280x800")
            
        self.root.configure(bg=COLOR_BG_DARK)
        
        # Configuration
        self.cell_size = 50 # Slightly smaller for better fit
        self.width = 10
        self.height = 10
        self.path_overlay = []
        
        # Data
        self.env = Environment(width=self.width, height=self.height)
        self.robot = Robot("RoboPro", (0, 9), self.env)
        
        self.setup_styles()
        self.create_layout()
        self.setup_environment()
        
        # Initial Render
        self.draw_grid()
        self.log("System Initialized. Ready for commands.", "system")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Base Configuration
        style.configure(".", 
                        background=COLOR_BG_DARK, 
                        foreground=COLOR_FG_PRIMARY, 
                        fieldbackground=COLOR_BG_PANEL,
                        font=("Segoe UI", 10))
        
        # Frames
        style.configure("Panel.TFrame", background=COLOR_BG_PANEL)
        style.configure("Card.TFrame", background=COLOR_BG_CARD, relief="flat")
        
        # Buttons
        style.configure("Accent.TButton", 
                        background=COLOR_ACCENT, 
                        foreground="white", 
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0,
                        padding=8)
        style.map("Accent.TButton", 
                  background=[('active', COLOR_ACCENT_HOVER)],
                  relief=[('pressed', 'flat')])
        
        style.configure("Secondary.TButton",
                        background=COLOR_BG_PANEL,
                        foreground=COLOR_FG_PRIMARY,
                        borderwidth=1,
                        relief="solid",
                        bordercolor=COLOR_ACCENT)
        style.map("Secondary.TButton", background=[('active', '#333333')])

        # Labels
        style.configure("Header.TLabel", 
                        font=("Segoe UI", 12, "bold"), 
                        background=COLOR_BG_CARD, 
                        foreground=COLOR_ACCENT)
        
        style.configure("SubHeader.TLabel",
                        font=("Segoe UI", 9, "bold"),
                        background=COLOR_BG_CARD,
                        foreground=COLOR_FG_SECONDARY)
        
        style.configure("Info.TLabel",
                        font=("Consolas", 10),
                        background=COLOR_BG_CARD,
                        foreground=COLOR_SUCCESS)

        # Checkbuttons
        style.configure("TCheckbutton", 
                        background=COLOR_BG_CARD, 
                        foreground=COLOR_FG_PRIMARY,
                        font=("Segoe UI", 10))
                        
        # Combobox
        style.configure("TCombobox", 
                        fieldbackground=COLOR_BG_PANEL, 
                        background=COLOR_BG_PANEL, 
                        foreground=COLOR_FG_PRIMARY,
                        arrowcolor=COLOR_ACCENT)

    def create_layout(self):
        # Main Layout Container (fills window)
        container = tk.Frame(self.root, bg=COLOR_BG_DARK)
        container.pack(fill=tk.BOTH, expand=True)

        # --- LEFT: MAP VISUALIZATION ---
        # Make this expandable
        self.canvas_frame = tk.Frame(container, bg=COLOR_BG_DARK)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(self.canvas_frame, text="LIVE SIMULATION MAP", 
                 font=("Segoe UI", 14, "bold"),
                 bg=COLOR_BG_DARK, fg=COLOR_FG_SECONDARY).pack(anchor="n", pady=(0, 10))
        
        # Center the canvas
        canvas_container = tk.Frame(self.canvas_frame, bg=COLOR_BG_DARK)
        canvas_container.pack(expand=True, fill=tk.BOTH)
        
        self.canvas = tk.Canvas(canvas_container, 
                                width=self.width*self.cell_size, 
                                height=self.height*self.cell_size,
                                bg=COLOR_BG_PANEL, 
                                highlightthickness=0)
        self.canvas.pack(anchor="center", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # --- RIGHT: CONTROL PANEL (SCROLLABLE) ---
        # Using a canvas to make the control panel scrollable for small screens
        self.right_panel_container = tk.Frame(container, bg=COLOR_BG_PANEL, width=400)
        self.right_panel_container.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_panel_container.pack_propagate(False)

        # Scrollbar for Right Panel
        self.panel_canvas = tk.Canvas(self.right_panel_container, bg=COLOR_BG_PANEL, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.right_panel_container, orient="vertical", command=self.panel_canvas.yview)
        self.control_panel = ttk.Frame(self.panel_canvas, style="Panel.TFrame")

        self.control_panel.bind(
            "<Configure>",
            lambda e: self.panel_canvas.configure(
                scrollregion=self.panel_canvas.bbox("all")
            )
        )

        self.panel_canvas.create_window((0, 0), window=self.control_panel, anchor="nw", width=380) # Adjust width for scrollbar
        self.panel_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.panel_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # --- PANEL CONTENT ---
        # 1. Info Card
        self.create_card_info()
        
        # 2. Controls Card
        self.create_card_controls()
        
        # 3. Intelligent Scheduling Card (NEW)
        self.create_card_scheduling()
        
        # 4. Logs Card
        self.create_card_logs()

        # Status Bar (Bottom of Root)
        self.status_var = tk.StringVar(value="System Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var,
                                   bg=COLOR_ACCENT, fg="white",
                                   anchor="w", padx=10, font=("Segoe UI", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_card_info(self):
        card = ttk.Frame(self.control_panel, style="Card.TFrame", padding=15)
        card.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(card, text="ROBOT STATUS", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        
        # Grid layout for info
        info_frame = ttk.Frame(card, style="Card.TFrame")
        info_frame.pack(fill=tk.X)
        
        self.lbl_battery = ttk.Label(info_frame, text="Battery: 100%", style="Info.TLabel")
        self.lbl_battery.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        self.lbl_pos = ttk.Label(info_frame, text="Pos: (0, 0)", style="Info.TLabel")
        self.lbl_pos.grid(row=0, column=1, sticky="w")

    def create_card_controls(self):
        card = ttk.Frame(self.control_panel, style="Card.TFrame", padding=15)
        card.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(card, text="MANUAL CONTROLS", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        
        # Task Selection
        ttk.Label(card, text="Pickup From:", style="SubHeader.TLabel").pack(anchor="w")
        self.pickup_var = tk.StringVar()
        self.pickup_combo = ttk.Combobox(card, textvariable=self.pickup_var, state="readonly")
        self.pickup_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(card, text="Deliver To:", style="SubHeader.TLabel").pack(anchor="w")
        self.dropoff_var = tk.StringVar()
        self.dropoff_combo = ttk.Combobox(card, textvariable=self.dropoff_var, state="readonly")
        self.dropoff_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Algorithm
        ttk.Label(card, text="Algorithm:", style="SubHeader.TLabel").pack(anchor="w")
        self.algo_var = tk.StringVar(value="A*")
        algo_combo = ttk.Combobox(card, textvariable=self.algo_var, values=["A*", "BFS", "DFS", "UCS", "Greedy BFS"], state="readonly")
        algo_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Action Buttons
        ttk.Button(card, text="EXECUTE SINGLE TASK", style="Accent.TButton", 
                   command=self.execute_task_thread).pack(fill=tk.X, pady=(0, 5))
        
        # Utility Buttons Row
        util_frame = ttk.Frame(card, style="Card.TFrame")
        util_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(util_frame, text="CHARGE", style="Secondary.TButton", 
                   command=self.go_charge_thread).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        ttk.Button(util_frame, text="RESET", style="Secondary.TButton", 
                   command=self.reset_simulation).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

    def create_card_scheduling(self):
        """New Interface for CSP Scheduling"""
        card = ttk.Frame(self.control_panel, style="Card.TFrame", padding=15)
        card.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(card, text="INTELLIGENT SCHEDULING", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        ttk.Label(card, text="Select tasks to prioritize:", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))
        
        self.check_clean_var = tk.BooleanVar()
        self.check_tea_var = tk.BooleanVar()
        self.check_charge_var = tk.BooleanVar()
        
        ttk.Checkbutton(card, text="Clean House", variable=self.check_clean_var, style="TCheckbutton").pack(anchor="w")
        ttk.Checkbutton(card, text="Serve Tea", variable=self.check_tea_var, style="TCheckbutton").pack(anchor="w")
        ttk.Checkbutton(card, text="Recharge Battery", variable=self.check_charge_var, style="TCheckbutton").pack(anchor="w")
        
        ttk.Button(card, text="PRIORITIZE & EXECUTE", style="Accent.TButton", 
                   command=self.schedule_tasks_thread).pack(fill=tk.X, pady=(15, 0))

    def create_card_logs(self):
        card = ttk.Frame(self.control_panel, style="Card.TFrame", padding=15)
        card.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(card, text="SYSTEM LOGS", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        
        log_frame = ttk.Frame(card, style="Card.TFrame")
        log_frame.pack(fill=tk.X)
        
        # Scrollbar for Logs
        log_scroll = ttk.Scrollbar(log_frame)
        self.log_text = tk.Text(log_frame, bg=COLOR_BG_DARK, fg=COLOR_FG_PRIMARY,
                                font=("Consolas", 8), relief="flat", height=8,
                                yscrollcommand=log_scroll.set)
        log_scroll.config(command=self.log_text.yview)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Log Tags
        self.log_text.tag_config("info", foreground="#61AFEF")
        self.log_text.tag_config("error", foreground="#E06C75")
        self.log_text.tag_config("success", foreground="#98C379")
        self.log_text.tag_config("system", foreground="#5C6370", font=("Consolas", 8, "italic"))
        self.log_text.tag_config("schedule", foreground="#E5C07B", font=("Consolas", 9, "bold"))

    def setup_environment(self):
        self.env.add_location('Kitchen', 0, 0)
        self.env.add_location('LivingRoom', 9, 9)
        self.env.add_location('Charger', 0, 9)
        self.env.add_location('Bedroom', 9, 0)
        
        # Obstacles (Wall)
        for y in range(3, 7):
            self.env.add_obstacle(4, y)
            
        # Update dropdowns
        locs = list(self.env.locations.keys())
        self.pickup_combo['values'] = locs
        self.dropoff_combo['values'] = locs

    def draw_grid(self):
        self.canvas.delete("all")
        
        # 1. Draw Grid Cells
        for y in range(self.height):
            for x in range(self.width):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Base color
                color = COLOR_GRID_EMPTY
                if (x, y) in self.env.obstacles:
                    color = COLOR_GRID_WALL
                
                # Draw cell
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                             fill=color, outline=COLOR_GRID_LINE)
                                             
                # Draw Location Label
                for name, pos in self.env.locations.items():
                    if pos == (x, y):
                        # Highlight location cell
                        self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, 
                                                     outline=COLOR_ACCENT, width=2)
                        # Icon/Text
                        self.canvas.create_text(x1+15, y1+20, text=name[:1], 
                                                fill=COLOR_ACCENT, font=("Segoe UI", 14, "bold"))
                        self.canvas.create_text((x1+x2)/2, y2-10, text=name, 
                                                fill=COLOR_FG_SECONDARY, font=("Segoe UI", 7))

        # 2. Draw Path Overlay
        if self.path_overlay:
            for i in range(len(self.path_overlay) - 1):
                p1 = self.path_overlay[i]
                p2 = self.path_overlay[i+1]
                
                cx1 = p1[0] * self.cell_size + self.cell_size/2
                cy1 = p1[1] * self.cell_size + self.cell_size/2
                cx2 = p2[0] * self.cell_size + self.cell_size/2
                cy2 = p2[1] * self.cell_size + self.cell_size/2
                
                self.canvas.create_line(cx1, cy1, cx2, cy2, fill=COLOR_ACCENT_HOVER, width=3, capstyle=tk.ROUND)
                
        # 3. Draw Robot (Glowing Effect)
        rx, ry = self.robot.position
        rx_center = rx * self.cell_size + self.cell_size/2
        ry_center = ry * self.cell_size + self.cell_size/2
        
        # Glow
        self.canvas.create_oval(rx_center-18, ry_center-18, rx_center+18, ry_center+18, 
                                fill="", outline=COLOR_ACCENT, width=1)
        # Body
        self.canvas.create_oval(rx_center-10, ry_center-10, rx_center+10, ry_center+10, 
                                fill=COLOR_ACCENT, outline="white")
                                
        self.lbl_pos.config(text=f"Pos: {self.robot.position}")

    def update_grid(self):
        """Thread-safe request to redraw the grid."""
        self.root.after(0, self.draw_grid)

    def draw_path_overlay(self, path):
        """Thread-safe request to draw path and redraw grid."""
        self.path_overlay = path
        self.update_grid()

    def log(self, message, tag="info"):
        timestamp = time.strftime("%H:%M:%S")
        self.root.after(0, lambda: self._insert_log(f"[{timestamp}] {message}\n", tag))

    def _insert_log(self, msg, tag):
        self.log_text.insert(tk.END, msg, tag)
        self.log_text.see(tk.END)
        
    def update_status(self, msg):
        # Update thread-safely
        self.root.after(0, lambda: self.status_var.set(msg))

    def update_battery_label(self):
        # Update thread-safely
        self.root.after(0, lambda: self.lbl_battery.config(text=f"Battery: {self.robot.battery}%"))

    def on_canvas_click(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.width and 0 <= y < self.height:
            if (x, y) == self.robot.position: return
            for pos in self.env.locations.values():
                if pos == (x, y): return
                
            if (x, y) not in self.env.obstacles:
                self.env.add_obstacle(x, y)
                self.log(f"User added obstacle at ({x}, {y})", "system")
                self.draw_grid()

    # --- THREADED ACTIONS ---
    def execute_task_thread(self):
        threading.Thread(target=self.execute_task, daemon=True).start()
        
    def go_charge_thread(self):
        threading.Thread(target=self.go_charge, daemon=True).start()
        
    def schedule_tasks_thread(self):
        threading.Thread(target=self.schedule_tasks, daemon=True).start()

    # --- LOGIC ---
    def schedule_tasks(self):
        """
        Implementation of CSP based scheduling logic.
        """
        selected_tasks = []
        if self.check_clean_var.get(): selected_tasks.append('Clean')
        if self.check_tea_var.get(): selected_tasks.append('Tea')
        if self.check_charge_var.get(): selected_tasks.append('Charge')
        
        if not selected_tasks:
            self.log("CSP: No tasks selected!", "warning")
            return
            
        self.log(f"CSP: Scheduling {selected_tasks}...", "system")
        self.update_status("Calculating Optimal Schedule...")
        
        # Define CSP
        # Basic domain: we have as many time slots as tasks
        num_tasks = len(selected_tasks)
        domains = {task: list(range(1, num_tasks + 1)) for task in selected_tasks}
        
        scheduler = CSP(selected_tasks, domains)
        scheduler.add_constraint(all_different_time_constraint)
        
        # Precedence Rule: Charge MUST be before Tea (Example rule)
        if 'Charge' in selected_tasks and 'Tea' in selected_tasks:
            scheduler.add_constraint(precedence_constraint('Charge', 'Tea'))
            self.log("Constraint: Charge BEFORE Tea", "system")
            
        schedule = scheduler.backtracking_search()
        
        if schedule:
            self.log("--- OPTIMAL SCHEDULE FOUND ---", "success")
            # Sort by time slot
            sorted_schedule = sorted(schedule.items(), key=lambda item: item[1])
            plan_str = " -> ".join([f"{time}: {task}" for task, time in sorted_schedule])
            self.log(plan_str, "schedule")
            
            # Execute the schedule automatically
            self.log("Executing Schedule...", "info")
            time.sleep(1)
            
            for task, _ in sorted_schedule:
                self.run_automated_task(task)
                time.sleep(1)
                
            self.log("All Scheduled Tasks Completed.", "success")
            self.update_status("Schedule Complete")
        else:
            self.log("CSP: No valid schedule found!", "error")
            self.update_status("Scheduling Failed")

    def run_automated_task(self, task_name):
        """Helper to map task names to robot actions."""
        self.log(f"Starting Task: {task_name}", "info")
        planner = GUIPlanner(self.robot, self.env, self)
        
        if task_name == 'Clean':
            # Go to LivingRoom and clean (simulated by pickup/drop)
            if planner.execute_subtask(('navigate', 'LivingRoom')):
                 self.log("Cleaning Living Room...", "info")
                 time.sleep(1)
            
        elif task_name == 'Tea':
             # Kitchen -> Bedroom
             if planner.execute_subtask(('navigate', 'Kitchen')):
                 planner.execute_subtask(('pick', 'Tea Cup'))
                 if planner.execute_subtask(('navigate', 'Bedroom')):
                     planner.execute_subtask(('drop', 'Tea Cup'))
                     
        elif task_name == 'Charge':
            if planner.execute_subtask(('navigate', 'Charger')):
                self.robot.charge()
                self.update_battery_label()

    def execute_task(self):
        pickup = self.pickup_var.get()
        dropoff = self.dropoff_var.get()
        algo = self.algo_var.get()
        
        if not pickup or not dropoff:
            self.log("Missing Task Parameters", "error")
            return
            
        self.log(f"Mission: {pickup} -> {dropoff} ({algo})", "info")
        self.path_overlay = []
        
        algo_func = a_star_search
        if algo == "BFS": algo_func = bfs_search
        elif algo == "DFS": algo_func = dfs_search
        elif algo == "UCS": algo_func = ucs_search
        elif algo == "Greedy BFS": algo_func = greedy_bfs_search
        
        planner = GUIPlanner(self.robot, self.env, self)
        
        # 1. Pickup
        if planner.execute_subtask(('navigate', pickup), search_algorithm=algo_func):
            planner.execute_subtask(('pick', 'Item'))
            
            # 2. Dropoff
            if planner.execute_subtask(('navigate', dropoff), search_algorithm=algo_func):
                planner.execute_subtask(('drop', 'Item'))
                self.log("Mission Accomplished.", "success")
                self.update_status("Mission Complete")
                self.path_overlay = []
                self.update_grid() # Thread-safe
            else:
                self.log("Mission Failed at Delivery", "error")
        else:
            self.log("Mission Failed at Pickup", "error")

    def reset_simulation(self):
        self.robot.position = (0, 9)
        self.robot.battery = 100
        self.robot.holding_item = None
        self.path_overlay = []
        self.update_battery_label()
        self.draw_grid()
        self.log("System Reset.", "system")
        self.update_status("System Reset")

    def go_charge(self):
        self.log("Initiating Charge Sequence...", "info")
        planner = GUIPlanner(self.robot, self.env, self)
        if planner.execute_subtask(('navigate', 'Charger')):
            self.robot.charge()
            self.update_battery_label()
            self.log("Robot Fully Charged.", "success")
        else:
            self.log("Failed to reach Charger!", "error")

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeServiceGUI(root)
    root.mainloop()
