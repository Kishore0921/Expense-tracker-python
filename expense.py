import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
import bcrypt
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Database Setup ---
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password BLOB)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, user_id INTEGER, category TEXT, amount REAL, date TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS income (id INTEGER PRIMARY KEY, user_id INTEGER, month TEXT, amount REAL, FOREIGN KEY(user_id) REFERENCES users(id))''')
conn.commit()

categories = ["Food & beverages", "Business", "Travelling", "Grocery", "Bills", "Entertainment", "Shopping", "Health", "Others"]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

current_user_id = None

# --- Expense Tracker App ---
def open_expense_tracker():
    login_window.destroy()
    root = tk.Tk()
    root.title("Expense Tracker")

    def add_expense():
        category = category_combobox.get()
        amount = amount_entry.get()
        date = date_entry.get()
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return
        if category and amount and date:
            cursor.execute("INSERT INTO expenses (user_id, category, amount, date) VALUES (?, ?, ?, ?)",
                           (current_user_id, category, amount, date))
            conn.commit()
            messagebox.showinfo("Success", "Expense added!")
            category_combobox.set("")
            amount_entry.delete(0, tk.END)
            date_entry.set_date("")
        else:
            messagebox.showwarning("Warning", "Fill all fields!")

    def show_expenses():
        cursor.execute("SELECT category, amount, date FROM expenses WHERE user_id=?", (current_user_id,))
        expenses = cursor.fetchall()
        expense_list.delete(0, tk.END)
        for exp in expenses:
            expense_list.insert(tk.END, f"{exp[0]} - ₹{exp[1]} on {exp[2]}")

    def add_income():
        month = month_combobox.get()
        amount = income_entry.get()
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return
        if month and amount:
            cursor.execute("INSERT INTO income (user_id, month, amount) VALUES (?, ?, ?)",
                           (current_user_id, month, amount))
            conn.commit()
            messagebox.showinfo("Success", "Income added!")
            month_combobox.set("")
            income_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Fill all fields!")

    def calculate_balance():
        cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (current_user_id,))
        total_income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (current_user_id,))
        total_expense = cursor.fetchone()[0] or 0
        balance_label.config(text=f"Yearly Balance: ₹{total_income - total_expense}")

    def clear_daily_expense():
        selected_date = date_entry.get()
        if selected_date:
            cursor.execute("DELETE FROM expenses WHERE user_id=? AND date=?", (current_user_id, selected_date))
            conn.commit()
            messagebox.showinfo("Success", f"Expenses for {selected_date} cleared!")
            show_expenses()

    def clear_monthly_income():
        selected_month = month_combobox.get()
        if selected_month:
            cursor.execute("DELETE FROM income WHERE user_id=? AND month=?", (current_user_id, selected_month))
            conn.commit()
            messagebox.showinfo("Success", f"Income for {selected_month} cleared!")

    def clear_all_expenses():
        cursor.execute("DELETE FROM expenses WHERE user_id=?", (current_user_id,))
        conn.commit()
        messagebox.showinfo("Success", "All expenses cleared!")
        show_expenses()

    def show_yearly_category_pie():
        cursor.execute("SELECT category, amount FROM expenses WHERE user_id=?", (current_user_id,))
        totals = defaultdict(float)
        for category, amount in cursor.fetchall():
            totals[category] += amount

        if not totals:
            messagebox.showinfo("No Data", "No expenses to show")
            return

        labels = list(totals.keys())
        sizes = list(totals.values())

        fig, ax = plt.subplots(figsize=(7, 6))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            autopct='%1.1f%%',
            startangle=90
        )

        ax.axis("equal")
        plt.title("Yearly Expenses by Category")

        # Add legend with categories
        ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(0.8,1))

        plt.show()

    # Layout
    tk.Label(root, text="Category").grid(row=0, column=0)
    tk.Label(root, text="Amount").grid(row=1, column=0)
    tk.Label(root, text="Date").grid(row=2, column=0)

    global category_combobox, amount_entry, date_entry, expense_list
    category_combobox = ttk.Combobox(root, values=categories, state="readonly")
    amount_entry = tk.Entry(root)
    date_entry = DateEntry(root)

    category_combobox.grid(row=0, column=1)
    amount_entry.grid(row=1, column=1)
    date_entry.grid(row=2, column=1)

    tk.Button(root, text="Add Expense", command=add_expense).grid(row=3, column=0, columnspan=2)
    tk.Button(root, text="Show Expenses", command=show_expenses).grid(row=4, column=0, columnspan=2)

    expense_list = tk.Listbox(root, width=50)
    expense_list.grid(row=5, column=0, columnspan=2)

    tk.Label(root, text="Month").grid(row=6, column=0)
    tk.Label(root, text="Income Amount").grid(row=7, column=0)

    global month_combobox, income_entry
    month_combobox = ttk.Combobox(root, values=months, state="readonly")
    income_entry = tk.Entry(root)

    month_combobox.grid(row=6, column=1)
    income_entry.grid(row=7, column=1)

    tk.Button(root, text="Add Income", command=add_income).grid(row=8, column=0, columnspan=2)
    tk.Button(root, text="Calculate Balance", command=calculate_balance).grid(row=9, column=0, columnspan=2)

    global balance_label
    balance_label = tk.Label(root, text="Yearly Balance: ₹0")
    balance_label.grid(row=10, column=0, columnspan=2)

    tk.Button(root, text="Clear Daily Expense", command=clear_daily_expense).grid(row=11, column=0, columnspan=2)
    tk.Button(root, text="Clear Monthly Income", command=clear_monthly_income).grid(row=12, column=0, columnspan=2)
    tk.Button(root, text="Clear All Expenses", command=clear_all_expenses).grid(row=13, column=0, columnspan=2)

    tk.Button(root, text="Show Yearly Pie Chart", command=show_yearly_category_pie).grid(row=14, column=0, columnspan=2)

    root.mainloop()

# --- Registration & Login ---
def register_window():
    login_window.withdraw()
    reg_win = tk.Toplevel()
    reg_win.title("Register")
    tk.Label(reg_win, text="Username").grid(row=0, column=0)
    tk.Label(reg_win, text="Password").grid(row=1, column=0)
    tk.Label(reg_win, text="Confirm Password").grid(row=2, column=0)
    username_entry = tk.Entry(reg_win)
    password_entry = tk.Entry(reg_win, show="*")
    confirm_entry = tk.Entry(reg_win, show="*")
    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)
    confirm_entry.grid(row=2, column=1)

    def register_user():
        username = username_entry.get().strip()
        password = password_entry.get()
        confirm = confirm_entry.get()
        if not username or not password or not confirm:
            messagebox.showwarning("Warning", "Fill all fields!")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        if len(password) != 8:
            messagebox.showerror("Error", "Password must be exactly 8 characters!")
            return
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            messagebox.showinfo("Success", "User registered!")
            reg_win.destroy()
            login_window.deiconify()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")

    tk.Button(reg_win, text="Register", command=register_user).grid(row=3, column=0, columnspan=2)
    tk.Button(reg_win, text="Back to Login", command=lambda: [reg_win.destroy(), login_window.deiconify()]).grid(row=4, column=0, columnspan=2)

def login():
    global current_user_id
    username = username_entry.get().strip()
    password = password_entry.get()
    if not username or not password:
        messagebox.showwarning("Warning", "Fill all fields!")
        return
    cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        user_id, stored_hash = result
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            current_user_id = user_id
            messagebox.showinfo("Success", f"Welcome {username}!")
            open_expense_tracker()
        else:
            messagebox.showerror("Error", "Incorrect password!")
    else:
        messagebox.showerror("Error", "Username not found!")

# --- Login Window ---
login_window = tk.Tk()
login_window.title("Login")

tk.Label(login_window, text="Username").grid(row=0, column=0)
tk.Label(login_window, text="Password").grid(row=1, column=0)

username_entry = tk.Entry(login_window)
password_entry = tk.Entry(login_window, show="*")

username_entry.grid(row=0, column=1)
password_entry.grid(row=1, column=1)

tk.Button(login_window, text="Login", command=login).grid(row=2, column=0, columnspan=2)
tk.Button(login_window, text="Register", command=register_window).grid(row=3, column=0, columnspan=2)

login_window.mainloop()
