"""
Smart Student Task & Deadline Tracker
A beginner-friendly Tkinter mini project.
Run: python smart_task_tracker.py
Data is saved automatically in tasks.csv in the same folder.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
from pathlib import Path

DATA_FILE = Path(__file__).with_name("tasks.csv")
FIELDS = ["title", "subject", "deadline", "priority", "status"]

class TaskTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Student Task & Deadline Tracker")
        self.root.geometry("900x600")
        self.root.minsize(760, 500)
        self.root.configure(bg="#f3f6fb")
        self.tasks = []
        self.build_ui()
        self.load_tasks()
        self.refresh_table()

    def build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=29, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        header = tk.Frame(self.root, bg="#183153", padx=20, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="SMART STUDENT TASK TRACKER",
                 font=("Arial", 19, "bold"), fg="white", bg="#183153").pack(anchor="w")
        tk.Label(header, text="Plan assignments • Track deadlines • Stay organized",
                 font=("Arial", 10), fg="#dce8f7", bg="#183153").pack(anchor="w", pady=(4, 0))

        form = tk.LabelFrame(self.root, text=" Add a new task ", bg="#f3f6fb",
                             font=("Arial", 10, "bold"), padx=12, pady=10)
        form.pack(fill="x", padx=18, pady=14)

        tk.Label(form, text="Task title", bg="#f3f6fb").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(form, width=26)
        self.title_entry.grid(row=1, column=0, padx=(0, 12), pady=5, sticky="ew")

        tk.Label(form, text="Subject", bg="#f3f6fb").grid(row=0, column=1, sticky="w")
        self.subject_entry = ttk.Entry(form, width=20)
        self.subject_entry.grid(row=1, column=1, padx=(0, 12), pady=5, sticky="ew")

        tk.Label(form, text="Deadline (YYYY-MM-DD)", bg="#f3f6fb").grid(row=0, column=2, sticky="w")
        self.date_entry = ttk.Entry(form, width=19)
        self.date_entry.grid(row=1, column=2, padx=(0, 12), pady=5, sticky="ew")
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        tk.Label(form, text="Priority", bg="#f3f6fb").grid(row=0, column=3, sticky="w")
        self.priority_box = ttk.Combobox(form, values=["High", "Medium", "Low"],
                                          state="readonly", width=10)
        self.priority_box.grid(row=1, column=3, padx=(0, 10), pady=5)
        self.priority_box.set("Medium")

        ttk.Button(form, text="＋ Add Task", command=self.add_task).grid(row=1, column=4, padx=4)
        for col in range(4):
            form.grid_columnconfigure(col, weight=1)

        controls = tk.Frame(self.root, bg="#f3f6fb")
        controls.pack(fill="x", padx=18, pady=(0, 8))
        tk.Label(controls, text="Show:", bg="#f3f6fb", font=("Arial", 10, "bold")).pack(side="left")
        self.filter_box = ttk.Combobox(controls, values=["All", "Pending", "Completed"],
                                       state="readonly", width=12)
        self.filter_box.set("All")
        self.filter_box.pack(side="left", padx=8)
        self.filter_box.bind("<<ComboboxSelected>>", lambda event: self.refresh_table())
        ttk.Button(controls, text="Mark Completed", command=self.complete_task).pack(side="right", padx=4)
        ttk.Button(controls, text="Delete Selected", command=self.delete_task).pack(side="right", padx=4)

        table_frame = tk.Frame(self.root, bg="#f3f6fb")
        table_frame.pack(fill="both", expand=True, padx=18, pady=5)
        columns = ("title", "subject", "deadline", "priority", "status")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {"title": "Task", "subject": "Subject", "deadline": "Deadline",
                    "priority": "Priority", "status": "Status"}
        widths = {"title": 260, "subject": 150, "deadline": 130, "priority": 100, "status": 110}
        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(col, width=widths[col], anchor="center")
        self.table.column("title", anchor="w")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.table.tag_configure("Completed", foreground="#18834a")
        self.table.tag_configure("Pending", foreground="#26384d")

        self.summary = tk.Label(self.root, text="", bg="#e5edf7", fg="#183153",
                                font=("Arial", 10, "bold"), padx=12, pady=9)
        self.summary.pack(fill="x", side="bottom")

    def add_task(self):
        title = self.title_entry.get().strip()
        subject = self.subject_entry.get().strip()
        deadline = self.date_entry.get().strip()
        priority = self.priority_box.get()
        if not title or not subject or not deadline:
            messagebox.showwarning("Missing information", "Please enter task, subject and deadline.")
            return
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Enter deadline in YYYY-MM-DD format, e.g. 2026-11-20.")
            return
        self.tasks.append({"title": title, "subject": subject, "deadline": deadline,
                           "priority": priority, "status": "Pending"})
        self.save_tasks()
        self.title_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.refresh_table()

    def complete_task(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select a task", "Choose a task from the table first.")
            return
        index = int(selected[0])
        visible = self.visible_tasks()
        task = visible[index]
        task["status"] = "Completed"
        self.save_tasks()
        self.refresh_table()

    def delete_task(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select a task", "Choose a task to delete.")
            return
        index = int(selected[0])
        task = self.visible_tasks()[index]
        self.tasks.remove(task)
        self.save_tasks()
        self.refresh_table()

    def visible_tasks(self):
        mode = self.filter_box.get()
        if mode == "Pending":
            return [t for t in self.tasks if t["status"] == "Pending"]
        if mode == "Completed":
            return [t for t in self.tasks if t["status"] == "Completed"]
        return self.tasks

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        shown = self.visible_tasks()
        for i, task in enumerate(shown):
            self.table.insert("", "end", iid=str(i),
                              values=(task["title"], task["subject"], task["deadline"],
                                      task["priority"], task["status"]),
                              tags=(task["status"],))
        completed = sum(1 for t in self.tasks if t["status"] == "Completed")
        pending = len(self.tasks) - completed
        self.summary.config(text=f"Total tasks: {len(self.tasks)}     |     Pending: {pending}     |     Completed: {completed}")

    def save_tasks(self):
        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(self.tasks)

    def load_tasks(self):
        if DATA_FILE.exists():
            try:
                with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
                    self.tasks = list(csv.DictReader(file))
            except (OSError, csv.Error):
                messagebox.showwarning("Data file", "Could not read saved tasks. Starting with an empty list.")
                self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTracker(root)
    root.mainloop()
