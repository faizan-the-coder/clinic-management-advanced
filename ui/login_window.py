import customtkinter as ctk
from database.models import DoctorModel
from utils.helpers import UIHelpers, MessageHelpers
from config import UI_COLORS

class LoginWindow:
    def __init__(self, on_login_callback):
        self.on_login_callback = on_login_callback
        self.doctor_model = DoctorModel()

        # Create main window
        self.window = ctk.CTk()
        self.window.title("Login - Clinic Management System")
        self.window.geometry("450x450+100+100")
        self.window.resizable(False, False)

        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)

        self.setup_ui()
        self.window.mainloop()

    def setup_ui(self):
        # Main container
        main_frame = UIHelpers.create_rounded_frame(
            self.window, 
            fg_color=UI_COLORS['background'],
            corner_radius=0
        )
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = UIHelpers.create_title_label(
            main_frame,
            "Clinic Management System",
            text_color=UI_COLORS['primary']
        )
        title_label.grid(row=0, column=0, pady=(20, 10))

        subtitle_label = UIHelpers.create_subtitle_label(
            main_frame,
            "Doctor Login",
            text_color=UI_COLORS['text']
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 30))

        # Login form
        form_frame = UIHelpers.create_rounded_frame(
            main_frame,
            fg_color=UI_COLORS['card'],
            corner_radius=15,
            width=350,
            height=200
        )
        form_frame.grid(row=2, column=0, pady=(0, 20))
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_propagate(False)

        # Username field
        username_label = UIHelpers.create_normal_label(
            form_frame,
            "Username:",
            text_color=UI_COLORS['text']
        )
        username_label.grid(row=0, column=0, sticky="w", padx=30, pady=(30, 5))

        self.username_entry = UIHelpers.create_styled_entry(
            form_frame,
            placeholder_text="Enter username",
            width=290
        )
        self.username_entry.grid(row=1, column=0, padx=30, pady=(0, 15))

        # Password field
        password_label = UIHelpers.create_normal_label(
            form_frame,
            "Password:",
            text_color=UI_COLORS['text']
        )
        password_label.grid(row=2, column=0, sticky="w", padx=30, pady=(0, 5))

        self.password_entry = UIHelpers.create_styled_entry(
            form_frame,
            placeholder_text="Enter password",
            show="*",
            width=290
        )
        self.password_entry.grid(row=3, column=0, padx=30, pady=(0, 30))

        # Bind Enter key to login
        self.window.bind('<Return>', lambda event: self.login())

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)

        login_btn = UIHelpers.create_styled_button(
            button_frame,
            "Login",
            command=self.login,
            fg_color=UI_COLORS['primary'],
            hover_color=UI_COLORS['hover'],
            width=150,
            height=40
        )
        login_btn.grid(row=0, column=0, padx=10)



        # Focus on username entry
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validate inputs
        if not username or not password:
            MessageHelpers.show_error("Login Error", "Please enter both username and password",parent=self.window)
            return

        # Authenticate
        success, doctor_info = self.doctor_model.authenticate_doctor(username, password)

        if success and doctor_info:
            MessageHelpers.show_success("Success", f"Welcome, Dr. {doctor_info['doctor_name']}!",parent=self.window)
            self.window.destroy()
            if self.on_login_callback:
                self.on_login_callback(doctor_info)
        else:
            MessageHelpers.show_error("Login Error", "Invalid username or password",parent=self.window)
            self.password_entry.delete(0, 'end')

    def destroy(self):
        self.window.destroy()
