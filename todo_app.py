import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")
CATEGORIES = ["Work", "Personal", "Study", "Health", "Finance", "Other"]


def load_tasks():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_tasks(tasks):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def parse_due(date_str, time_str):
    """Return a datetime. Time is optional (defaults to end of day)."""
    date_str, time_str = date_str.strip(), time_str.strip()
    if time_str:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.replace(hour=23, minute=59)


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("My To-Do List")
        self.geometry("960x560")
        self.tasks = load_tasks()
        self.build_form()
        self.build_list()
        self.refresh()

    # ---------- UI ----------
    def build_form(self):
        f = ttk.LabelFrame(self, text="New task", padding=10)
        f.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(f, text="Heading").pack(anchor="w")
        self.title_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.title_var, width=30).pack(pady=(0, 8))

        ttk.Label(f, text="Due date (YYYY-MM-DD)").pack(anchor="w")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(f, textvariable=self.date_var, width=30).pack(pady=(0, 8))

        ttk.Label(f, text="Due time (HH:MM, optional)").pack(anchor="w")
        self.time_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.time_var, width=30).pack(pady=(0, 8))

        ttk.Label(f, text="Category").pack(anchor="w")
        self.cat_var = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(f, textvariable=self.cat_var, values=CATEGORIES, width=27).pack(pady=(0, 8))

        ttk.Label(f, text="Description").pack(anchor="w")
        self.desc = tk.Text(f, width=30, height=6, wrap="word")
        self.desc.pack(pady=(0, 10))

        ttk.Button(f, text="Add task", command=self.add_task).pack(fill="x")

    def build_list(self):
        r = ttk.Frame(self, padding=(0, 10, 10, 10))
        r.pack(side="right", fill="both", expand=True)

        top = ttk.Frame(r)
        top.pack(fill="x", pady=(0, 6))
        ttk.Label(top, text="Filter:").pack(side="left")
        self.filter_var = tk.StringVar(value="All")
        cb = ttk.Combobox(top, textvariable=self.filter_var, values=["All"] + CATEGORIES,
                          width=14, state="readonly")
        cb.pack(side="left", padx=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.hide_done = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Hide completed", variable=self.hide_done,
                        command=self.refresh).pack(side="left", padx=10)

        cols = ("done", "title", "due", "category", "desc")
        self.tree = ttk.Treeview(r, columns=cols, show="headings", selectmode="browse")
        for c, t, w in [("done", "✓", 40), ("title", "Task", 190), ("due", "Due", 130),
                        ("category", "Category", 90), ("desc", "Description", 280)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("overdue", foreground="#c0392b")
        self.tree.tag_configure("done", foreground="#999999")

        btns = ttk.Frame(r)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Mark done / undo", command=self.toggle_done).pack(side="left")
        ttk.Button(btns, text="Delete", command=self.delete_task).pack(side="left", padx=6)

    # ---------- Logic ----------
    def add_task(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Missing heading", "Please enter a task heading.")
            return
        try:
            due = parse_due(self.date_var.get(), self.time_var.get())
        except ValueError:
            messagebox.showerror("Invalid date/time", "Use YYYY-MM-DD and HH:MM (24-hour).")
            return
        self.tasks.append({
            "id": int(datetime.now().timestamp() * 1000),
            "title": title,
            "due": due.isoformat(timespec="minutes"),
            "has_time": bool(self.time_var.get().strip()),
            "category": self.cat_var.get().strip() or "Other",
            "description": self.desc.get("1.0", "end").strip(),
            "done": False,
        })
        save_tasks(self.tasks)
        self.title_var.set("")
        self.time_var.set("")
        self.desc.delete("1.0", "end")
        self.refresh()

    def selected_task(self):
        sel = self.tree.selection()
        if not sel:
            return None
        tid = int(sel[0])
        return next((t for t in self.tasks if t["id"] == tid), None)

    def toggle_done(self):
        t = self.selected_task()
        if t:
            t["done"] = not t["done"]
            save_tasks(self.tasks)
            self.refresh()

    def delete_task(self):
        t = self.selected_task()
        if t and messagebox.askyesno("Delete", f"Delete '{t['title']}'?"):
            self.tasks.remove(t)
            save_tasks(self.tasks)
            self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        now = datetime.now()
        flt = self.filter_var.get()
        for t in sorted(self.tasks, key=lambda x: (x["done"], x["due"])):
            if flt != "All" and t["category"] != flt:
                continue
            if self.hide_done.get() and t["done"]:
                continue
            due = datetime.fromisoformat(t["due"])
            due_txt = due.strftime("%d %b %Y, %H:%M") if t.get("has_time") else due.strftime("%d %b %Y")
            tags = ()
            if t["done"]:
                tags = ("done",)
            elif due < now:
                tags = ("overdue",)
            self.tree.insert("", "end", iid=str(t["id"]), tags=tags,
                             values=("✔" if t["done"] else "", t["title"], due_txt,
                                     t["category"], t["description"].replace("\n", " ")))


if __name__ == "__main__":
    TodoApp().mainloop()
