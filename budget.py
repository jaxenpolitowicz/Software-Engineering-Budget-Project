import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from collections import defaultdict

#Matplotlib
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATA_FILE = "budget_data.json"
DEFAULT_CATEGORIES = {
    "Food": 300.0,
    "Transport": 150.0,
    "Bills": 400.0,
    "Entertainment": 100.0,
    "Other": 100.0,
}


# Model: data handling
class BudgetModel:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.categories = {}   # name -> { "limit": float }
        self.expenses = []     # list of { "category","amount","desc","date" }
        self.load()

    def load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                #tolerate older formats
                cats = data.get("categories", [])
                if isinstance(cats, dict):
                    #maybe saved as dict name->limit
                    self.categories = {k: {"limit": float(v)} for k, v in cats.items()}
                else:
                    self.categories = {c["name"]: {"limit": float(c["limit"])} for c in cats}
                self.expenses = data.get("expenses", [])
            except Exception:
                #fallback to defaults if file corrupt
                self._load_defaults()
        else:
            self._load_defaults()

    def _load_defaults(self):
        self.categories = {name: {"limit": float(limit)} for name, limit in DEFAULT_CATEGORIES.items()}
        self.expenses = []
        self.save()

    def save(self):
        try:
            data = {
                #store categories as list of objects for readability
                "categories": [{"name": name, "limit": info["limit"]} for name, info in self.categories.items()],
                "expenses": self.expenses
            }
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showwarning("Save Error", f"Could not save data: {e}")

    def add_category(self, name, limit):
        key = name.strip()
        if not key:
            raise ValueError("Category name cannot be empty.")
        #case-insensitive duplicate prevention
        for existing in list(self.categories.keys()):
            if existing.lower() == key.lower():
                raise ValueError(f"Category '{existing}' already exists (case-insensitive match).")
        self.categories[key] = {"limit": float(limit)}
        self.save()

    def edit_limit(self, name, new_limit):
        if name not in self.categories:
            raise ValueError("Category not found.")
        self.categories[name]["limit"] = float(new_limit)
        self.save()

    def add_expense(self, category, amount, desc=""):
        if category not in self.categories:
            raise ValueError("Category does not exist.")
        e = {"category": category, "amount": float(amount), "desc": desc, "date": datetime.now().isoformat()}
        self.expenses.append(e)
        self.save()

    def get_spent_per_category(self):
        totals = defaultdict(float)
        for e in self.expenses:
            totals[e["category"]] += float(e["amount"])
        #ensure all categories present
        for c in self.categories.keys():
            totals.setdefault(c, 0.0)
        return dict(totals)

    def get_category_summary(self, category):
        spent = sum(float(e["amount"]) for e in self.expenses if e["category"] == category)
        limit = float(self.categories.get(category, {}).get("limit", 0.0))
        remaining = limit - spent
        return {"spent": spent, "limit": limit, "remaining": remaining}

    def get_expenses_for_category(self, category):
        return [e for e in self.expenses if e["category"] == category]

    def clear_all(self):
        if os.path.exists(self.data_file):
            try:
                os.remove(self.data_file)
            except Exception:
                pass
        self._load_defaults()



# View/Controller: Tkinter GUI
class SmartBudgetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartBudget")
        self.model = BudgetModel()

        self.build_ui()
        self.populate_category_widgets()
        self.refresh_all()

    def build_ui(self):
        # Top frame: add category / add expense
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=8, pady=6)

        # Add Category
        cat_frame = tk.LabelFrame(top, text="Add Category")
        cat_frame.pack(side="left", padx=6)
        tk.Label(cat_frame, text="Name:").grid(row=0, column=0, sticky="e")
        tk.Label(cat_frame, text="Limit:").grid(row=1, column=0, sticky="e")
        self.entry_cat_name = tk.Entry(cat_frame, width=18)
        self.entry_cat_limit = tk.Entry(cat_frame, width=18)
        self.entry_cat_name.grid(row=0, column=1, padx=4, pady=2)
        self.entry_cat_limit.grid(row=1, column=1, padx=4, pady=2)
        tk.Button(cat_frame, text="Add Category", command=self.on_add_category).grid(row=2, column=0, columnspan=2, pady=6)

        # Add Expense
        exp_frame = tk.LabelFrame(top, text="Add Expense")
        exp_frame.pack(side="left", padx=6)
        tk.Label(exp_frame, text="Category:").grid(row=0, column=0, sticky="e")
        tk.Label(exp_frame, text="Amount:").grid(row=1, column=0, sticky="e")
        tk.Label(exp_frame, text="Description:").grid(row=2, column=0, sticky="e")

        self.cat_var = tk.StringVar()
        self.combo_cat = ttk.Combobox(exp_frame, textvariable=self.cat_var, state="readonly", width=20)
        self.combo_cat.grid(row=0, column=1, padx=4, pady=2)

        self.entry_amount = tk.Entry(exp_frame, width=18)
        self.entry_desc = tk.Entry(exp_frame, width=18)
        self.entry_amount.grid(row=1, column=1, padx=4, pady=2)
        self.entry_desc.grid(row=2, column=1, padx=4, pady=2)
        tk.Button(exp_frame, text="Add Expense", command=self.on_add_expense).grid(row=3, column=0, columnspan=2, pady=6)

        # Middle: charts and summary
        middle = tk.Frame(self.root)
        middle.pack(fill="both", expand=True, padx=8, pady=6)

        # Matplotlib figure
        self.fig = Figure(figsize=(8, 3.6), tight_layout=True)
        self.ax_left = self.fig.add_subplot(1, 2, 1)
        self.ax_right = self.fig.add_subplot(1, 2, 2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=middle)
        self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

        # Right panel: selector, summary, listbox
        right = tk.Frame(middle)
        right.pack(side="left", fill="y", padx=6)

        tk.Label(right, text="Select Category:").pack(pady=(4,0))
        self.select_var = tk.StringVar()
        self.select_combo = ttk.Combobox(right, textvariable=self.select_var, state="readonly", width=24)
        self.select_combo.pack()
        self.select_combo.bind("<<ComboboxSelected>>", lambda e: self.update_category_chart())

        tk.Button(right, text="Edit Selected Limit", command=self.on_edit_limit).pack(pady=6)
        tk.Button(right, text="Refresh Charts", command=self.refresh_all).pack(pady=2)
        tk.Button(right, text="Clear All Data", command=self.on_clear_data).pack(pady=(10,2))

        tk.Label(right, text="Category Summary:").pack(pady=(10,0))
        self.summary_box = tk.Text(right, height=6, width=36, state="disabled")
        self.summary_box.pack(pady=4)

        tk.Label(right, text="Transactions (selected):").pack(pady=(6,0))
        self.tx_list = tk.Listbox(right, width=48, height=10)
        self.tx_list.pack(pady=4)

   
    # Event handlers
    def on_add_category(self):
        name = self.entry_cat_name.get().strip()
        limit_str = self.entry_cat_limit.get().strip()
        if not name or not limit_str:
            messagebox.showerror("Input Error", "Both name and limit are required.")
            return
        try:
            limit = float(limit_str)
            self.model.add_category(name, limit)
        except ValueError as e:
            messagebox.showerror("Error", f"{e}")
            return
        self.entry_cat_name.delete(0, tk.END)
        self.entry_cat_limit.delete(0, tk.END)
        self.populate_category_widgets()
        self.refresh_all()
        messagebox.showinfo("Added", f"Category '{name}' added with limit ${limit:.2f}.")

    def on_add_expense(self):
        cat = self.cat_var.get()
        amt_str = self.entry_amount.get().strip()
        desc = self.entry_desc.get().strip()
        if not cat or not amt_str:
            messagebox.showerror("Input Error", "Category and amount are required.")
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError("Amount must be positive.")
            self.model.add_expense(cat, amt, desc)
        except Exception as e:
            messagebox.showerror("Error", f"{e}")
            return
        self.entry_amount.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.refresh_all()
        messagebox.showinfo("Added", f"${amt:.2f} added to {cat}.")

    def on_edit_limit(self):
        cat = self.select_combo.get()
        if not cat:
            messagebox.showerror("Error", "Select a category to edit.")
            return
        current = self.model.categories.get(cat, {}).get("limit", 0.0)
        new_limit_str = simpledialog.askstring("Edit Limit", f"Category '{cat}' current limit ${current:.2f}\nEnter new limit:")
        if new_limit_str is None:
            return
        try:
            new_limit = float(new_limit_str)
            self.model.edit_limit(cat, new_limit)
        except Exception as e:
            messagebox.showerror("Error", f"{e}")
            return
        self.refresh_all()
        messagebox.showinfo("Updated", f"Limit for '{cat}' set to ${new_limit:.2f}.")

    def on_clear_data(self):
        if messagebox.askyesno("Confirm", "Delete saved data and reset to defaults?"):
            self.model.clear_all()
            self.populate_category_widgets()
            self.refresh_all()
            messagebox.showinfo("Reset", "Data reset to defaults.")

    
    # UI helpers
    def populate_category_widgets(self):
        names = sorted(self.model.categories.keys())
        self.combo_cat["values"] = names
        self.select_combo["values"] = names
        # set defaults if nothing selected
        if names:
            if not self.combo_cat.get() or self.combo_cat.get() not in names:
                self.combo_cat.set(names[0])
            if not self.select_combo.get() or self.select_combo.get() not in names:
                self.select_combo.set(names[0])

    def refresh_all(self):
        self.populate_category_widgets()
        self.update_spending_chart()
        self.update_category_chart()

    def update_spending_chart(self):
        self.ax_left.clear()
        totals = self.model.get_spent_per_category()

        # Sort: highest first
        items = sorted(totals.items(), key=lambda x: -x[1])
        labels = [name for name, _ in items]
        sizes = [amt for _, amt in items]

        if sum(sizes) == 0:
            self.ax_left.text(0.5, 0.5, "No spending recorded", ha="center", va="center")
            self.canvas.draw_idle()
            return

        # Clean pie chart with no overlapping labels
        wedges, _ = self.ax_left.pie(
            sizes,
            startangle=90
        )

        # Add legend on the left side (no overlap possible)
        legend_labels = [f"{name}: ${amt:.2f}" for name, amt in items]
        self.ax_left.legend(
            wedges,
            legend_labels,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1.05, 0.5)
        )

        self.ax_left.set_title("Spending per Category")
        self.canvas.draw_idle()


    def update_category_chart(self):
        self.ax_right.clear()
        cat = self.select_combo.get()
        if not cat or cat not in self.model.categories:
            self.ax_right.text(0.5, 0.5, "No category selected", ha="center", va="center")
            self.canvas.draw_idle()
            self.update_summary_box(None)
            self.update_tx_list(None)
            return
        summary = self.model.get_category_summary(cat)
        spent = summary["spent"]
        limit = summary["limit"]
        remaining = max(limit - spent, 0.0)
        if limit <= 0:
            # only show spent slice
            if spent <= 0:
                self.ax_right.text(0.5, 0.5, "No data for this category", ha="center", va="center")
            else:
                self.ax_right.pie([spent], labels=[f"Spent\n${spent:.2f}"], startangle=90)
        else:
            sizes = [spent, remaining]
            labels = [f"Spent\n${spent:.2f}", f"Remaining\n${remaining:.2f}"]
            explode = (0.05, 0)
            self.ax_right.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, explode=explode)
        self.ax_right.set_title(f"Spent vs Remaining: {cat}")
        self.canvas.draw_idle()
        self.update_summary_box(cat)
        self.update_tx_list(cat)

    def update_summary_box(self, cat):
        self.summary_box.config(state="normal")
        self.summary_box.delete("1.0", tk.END)
        if cat and cat in self.model.categories:
            s = self.model.get_category_summary(cat)
            lines = [
                f"Category: {cat}",
                f"Limit: ${s['limit']:.2f}",
                f"Spent: ${s['spent']:.2f}",
                f"Remaining: ${s['remaining']:.2f}",
            ]
        else:
            totals = self.model.get_spent_per_category()
            total_spent = sum(totals.values())
            lines = [f"Total spent: ${total_spent:.2f}", f"Categories: {len(self.model.categories)}"]
        self.summary_box.insert(tk.END, "\n".join(lines))
        self.summary_box.config(state="disabled")

    def update_tx_list(self, cat):
        self.tx_list.delete(0, tk.END)
        if cat and cat in self.model.categories:
            exps = self.model.get_expenses_for_category(cat)
            for e in exps:
                dt = e.get("date", "")[:19].replace("T", " ")
                self.tx_list.insert(tk.END, f"{dt} | ${float(e['amount']):.2f} | {e.get('desc','')}")
        else:
            # show recent global
            for e in list(reversed(self.model.expenses[-100:])):
                dt = e.get("date", "")[:19].replace("T", " ")
                self.tx_list.insert(tk.END, f"{dt} | {e['category']} | ${float(e['amount']):.2f} | {e.get('desc','')}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartBudgetGUI(root)
    root.mainloop()
