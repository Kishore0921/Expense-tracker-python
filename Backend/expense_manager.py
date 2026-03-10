import matplotlib.pyplot as plt
from Backend.db import get_connection

def get_yearly_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get total Income
    cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (user_id,))
    income = cursor.fetchone()[0] or 0
    
    # Get total Expenses
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,))
    expenses = cursor.fetchone()[0] or 0
    
    conn.close()
    return income, expenses, (income - expenses)

def show_pie_chart(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (user_id,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        return False

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(6, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title("Expense Distribution")
    plt.show()
    return True