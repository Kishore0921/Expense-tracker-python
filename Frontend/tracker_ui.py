import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from Backend.db import get_connection

class TrackerWindow:
    def __init__(self, user_id):
        self.root = tk.Tk()
        self.user_id = user_id
        self.root.title("Expense Tracker Pro")
        self.root.geometry("800x600")

        # Keep shared options close to the UI code
        self.categories = [
            "Food & beverages",
            "Business",
            "Travelling",
            "Grocery",
            "Bills",
            "Entertainment",
            "Shopping",
            "Health",
            "Others",
        ]
        self.months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        # This builds the actual visual elements
        self.setup_ui()
        
    def setup_ui(self):
        # 1. Main Container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # 2. Input Section (Top)
        input_frame = ttk.LabelFrame(main_frame, text="Add Transaction", padding="10")
        input_frame.pack(fill="x", pady=10)

        ttk.Label(input_frame, text="Category:").grid(row=0, column=0, padx=5)
        self.cat_cb = ttk.Combobox(input_frame, values=self.categories, state="readonly")
        self.cat_cb.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Amount:").grid(row=0, column=2, padx=5)
        self.amt_entry = ttk.Entry(input_frame)
        self.amt_entry.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Date:").grid(row=0, column=4, padx=5)
        self.date_ent = DateEntry(input_frame)
        self.date_ent.grid(row=0, column=5, padx=5)

        ttk.Button(input_frame, text="Add Expense", command=self.add_expense).grid(row=0, column=6, padx=10)
        ttk.Button(input_frame, text="Show Expenses", command=self.load_expenses).grid(row=0, column=7, padx=10)

        # 3. Table Section (Bottom)
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)

        # Professional Treeview table
        self.tree = ttk.Treeview(table_frame, columns=("Category", "Amount", "Date"), show="headings")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount (₹)")
        self.tree.heading("Date", text="Date")
        self.tree.column("Category", width=180)
        self.tree.column("Amount", width=120, anchor="e")
        self.tree.column("Date", width=120)

        # Add a scrollbar to the table
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 4. Income + Controls Section
        controls_frame = ttk.Frame(main_frame, padding="10")
        controls_frame.pack(fill="x")

        ttk.Label(controls_frame, text="Month:").grid(row=0, column=0, padx=5, sticky="w")
        self.month_cb = ttk.Combobox(controls_frame, values=self.months, state="readonly")
        self.month_cb.grid(row=0, column=1, padx=5)

        ttk.Label(controls_frame, text="Income Amount:").grid(row=0, column=2, padx=5, sticky="w")
        self.income_entry = ttk.Entry(controls_frame)
        self.income_entry.grid(row=0, column=3, padx=5)

        ttk.Button(controls_frame, text="Add Income", command=self.add_income).grid(row=0, column=4, padx=10)
        ttk.Button(controls_frame, text="Calculate Balance", command=self.calculate_balance).grid(row=0, column=5, padx=10)

        self.balance_label = ttk.Label(controls_frame, text="Yearly Balance: ₹0")
        self.balance_label.grid(row=0, column=6, padx=10)

        ttk.Button(controls_frame, text="Clear Daily Expense", command=self.clear_daily_expense).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(controls_frame, text="Clear Monthly Income", command=self.clear_monthly_income).grid(row=1, column=2, columnspan=2, pady=10, sticky="ew")
        ttk.Button(controls_frame, text="Clear All Expenses", command=self.clear_all_expenses).grid(row=1, column=4, columnspan=2, pady=10, sticky="ew")
        ttk.Button(controls_frame, text="Show Yearly Pie Chart", command=self.show_yearly_pie_chart).grid(row=1, column=6, padx=10, pady=10, sticky="ew")

        # Load any existing data
        self.load_expenses()
        self.calculate_balance()

    def get_db(self):
        return get_connection()

    def add_expense(self):
        category = self.cat_cb.get().strip()
        amount_str = self.amt_entry.get().strip()
        date = self.date_ent.get()  # DateEntry returns string

        if not category or not amount_str or not date:
            messagebox.showwarning("Warning", "Please fill all fields")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (user_id, category, amount, date) VALUES (?, ?, ?, ?)",
                       (self.user_id, category, amount, date))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Expense added!")
        self.cat_cb.set("")
        self.amt_entry.delete(0, tk.END)
        # Keep the selected date for convenience

        self.load_expenses()
        self.calculate_balance()

    def load_expenses(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT category, amount, date FROM expenses WHERE user_id=? ORDER BY date DESC", (self.user_id,))
        for category, amount, date in cursor.fetchall():
            self.tree.insert("", tk.END, values=(category, f"₹{amount:.2f}", date))
        conn.close()

    def add_income(self):
        month = self.month_cb.get().strip()
        amt_str = self.income_entry.get().strip()

        if not month or not amt_str:
            messagebox.showwarning("Warning", "Please fill all fields")
            return

        try:
            amount = float(amt_str)
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO income (user_id, month, amount) VALUES (?, ?, ?)",
                       (self.user_id, month, amount))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Income added!")
        self.month_cb.set("")
        self.income_entry.delete(0, tk.END)
        self.calculate_balance()

    def calculate_balance(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (self.user_id,))
        total_income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (self.user_id,))
        total_expense = cursor.fetchone()[0] or 0
        conn.close()

        balance = total_income - total_expense
        self.balance_label.config(text=f"Yearly Balance: ₹{balance:.2f}")

    def clear_daily_expense(self):
        selected_date = self.date_ent.get()
        if not selected_date:
            messagebox.showwarning("Warning", "Select a date to clear")
            return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE user_id=? AND date=?", (self.user_id, selected_date))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Expenses for {selected_date} cleared!")
        self.load_expenses()
        self.calculate_balance()

    def clear_monthly_income(self):
        selected_month = self.month_cb.get().strip()
        if not selected_month:
            messagebox.showwarning("Warning", "Select a month to clear")
            return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM income WHERE user_id=? AND month=?", (self.user_id, selected_month))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Income for {selected_month} cleared!")
        self.calculate_balance()

    def clear_all_expenses(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE user_id=?", (self.user_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "All expenses cleared!")
        self.load_expenses()
        self.calculate_balance()

    def show_yearly_pie_chart(self):
        from Backend.expense_manager import show_pie_chart

        if not show_pie_chart(self.user_id):
            messagebox.showinfo("No Data", "No expenses to show")

    def mainloop(self):
        self.root.mainloop()