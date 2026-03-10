import tkinter as tk
from tkinter import messagebox, ttk
from Backend.auth import verify_login, register_user
from Frontend.tracker_ui import TrackerWindow

class LoginWindow:
    def __init__(self):
        # Create the main root window
        self.root = tk.Tk()
        self.root.title("Expense Tracker - Login")
        self.root.geometry("350x300")
        
        # Call the UI setup method
        self.setup_ui()

    def setup_ui(self):
        """This is the method that was missing or renamed"""
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)

        ttk.Label(frame, text="Username").grid(row=0, column=0, pady=5, sticky="w")
        self.user_ent = ttk.Entry(frame)
        self.user_ent.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Password").grid(row=1, column=0, pady=5, sticky="w")
        self.pass_ent = ttk.Entry(frame, show="*")
        self.pass_ent.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Login", command=self.handle_login).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(frame, text="Register", command=self.handle_register).grid(row=3, column=0, columnspan=2, sticky="ew")

    def handle_login(self):
        username = self.user_ent.get().strip()
        password = self.pass_ent.get()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please fill all fields")
            return

        uid = verify_login(username, password)
        if uid:
            self.root.destroy()  # Close the login window
            # The TrackerWindow should be a Toplevel or a new Tk root
            app = TrackerWindow(uid)
            app.mainloop()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def handle_register(self):
        username = self.user_ent.get().strip()
        password = self.pass_ent.get()
        
        success, msg = register_user(username, password)
        if success:
            messagebox.showinfo("Success", "Account Created! You can now login.")
        else:
            messagebox.showwarning("Failed", msg)

    def mainloop(self):
        self.root.mainloop()