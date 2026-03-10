from Backend.db import init_db
from Frontend.login_ui import LoginWindow

def main():
    init_db()
    app = LoginWindow()
    app.mainloop()

if __name__ == "__main__":
    main()