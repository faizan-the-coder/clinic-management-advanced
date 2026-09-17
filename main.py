import customtkinter as ctk
import sys
from database.db_manager import DatabaseManager
from database.models import DoctorModel
from ui.doctor_registration import DoctorRegistrationWindow
from ui.login_window import LoginWindow
from ui.main_dashboard import MainDashboard

class ClinicManagementApp:
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.db_manager = DatabaseManager()
        self.doctor_model = DoctorModel()
        self.current_doctor = None

        # Initialize database
        self.init_database()

        # Check if doctor is registered
        if self.is_doctor_registered():
            self.show_login_window()
        else:
            self.show_registration_window()

    def init_database(self):
        try:
            if not self.db_manager.create_database():
                self.show_error("Database Error", "Failed to initialize database. Please check your MySQL connection.")
                sys.exit(1)
            print("✓ Database initialized successfully")
        except Exception as e:
            self.show_error("Database Error", f"Database initialization failed: {str(e)}")
            sys.exit(1)

    def is_doctor_registered(self):
        try:
            doctor = self.doctor_model.get_doctor_info()
            return doctor is not None
        except Exception as e:
            print(f"Error checking doctor registration: {e}")
            return False

    def show_registration_window(self):
        self.registration_window = DoctorRegistrationWindow(self.on_registration_complete)

    def show_login_window(self):
        self.login_window = LoginWindow(self.on_login_success)

    def show_main_dashboard(self):
        if self.current_doctor:
            self.dashboard = MainDashboard(self.current_doctor, self.on_logout)

    def on_registration_complete(self):
        # Close registration window and show login
        if hasattr(self, 'registration_window'):
            self.registration_window.destroy()
        self.show_login_window()

    def on_login_success(self, doctor_info):
        self.current_doctor = doctor_info
        # Close login window and show dashboard
        if hasattr(self, 'login_window'):
            self.login_window.destroy()
        self.show_main_dashboard()

    def on_logout(self):
        self.current_doctor = None
        # Close dashboard and show login
        if hasattr(self, 'dashboard'):
            self.dashboard.destroy()
        self.show_login_window()

    def show_error(self, title, message):
        import tkinter.messagebox as msgbox
        msgbox.showerror(title, message)

def main():
    try:
        app = ClinicManagementApp()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()












