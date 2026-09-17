import customtkinter as ctk
from database.models import DoctorModel
from utils.helpers import UIHelpers, ValidationHelpers, MessageHelpers
from config import UI_COLORS

class DoctorRegistrationWindow:
    def __init__(self, on_complete_callback):
        self.on_complete_callback = on_complete_callback
        self.doctor_model = DoctorModel()

        # Create main window
        self.window = ctk.CTk()
        self.window.title("Doctor Registration - Clinic Management System")
        self.window.geometry("600x660+10+10")
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
        title_label.grid(row=0, column=0, pady=(0, 10))

        subtitle_label = UIHelpers.create_subtitle_label(
            main_frame,
            "Doctor Registration",
            text_color=UI_COLORS['text']
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 30))

        # Registration form
        form_frame = UIHelpers.create_rounded_frame(
            main_frame,
            fg_color=UI_COLORS['card'],
            corner_radius=15
        )
        form_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        form_frame.grid_columnconfigure(1, weight=1)

        # Form fields
        fields = [
            ("Clinic Name:", "clinic_name"),
            ("Doctor Name:", "doctor_name"),
            ("Specialization:", "specialization"),
            ("Email:", "email"),
            ("Phone:", "phone"),
            ("Username:", "username"),
            ("Password:", "password")
        ]

        self.entries = {}

        for i, (label_text, field_name) in enumerate(fields):
            # Label
            label = UIHelpers.create_normal_label(
                form_frame,
                label_text,
                text_color=UI_COLORS['text']
            )
            label.grid(row=i, column=0, sticky="w", padx=20, pady=10)

            # Entry
            if field_name == "specialization":
                specializations = [
                    "General Medicine", "Pediatrics", "Cardiology", "Dermatology",
                    "Neurology", "Orthopedics", "Gynecology", "ENT",
                    "Ophthalmology", "Psychiatry", "Other"
                ]
                entry = UIHelpers.create_styled_combobox(
                    form_frame,
                    values=specializations,
                    width=300
                )
            elif field_name == "password":
                entry = UIHelpers.create_styled_entry(
                    form_frame,
                    placeholder_text="Enter password",
                    show="*",
                    width=300
                )
            else:
                entry = UIHelpers.create_styled_entry(
                    form_frame,
                    placeholder_text=f"Enter {label_text.lower()}",
                    width=300
                )

            entry.grid(row=i, column=1, sticky="ew", padx=20, pady=10)
            self.entries[field_name] = entry

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)

        register_btn = UIHelpers.create_styled_button(
            button_frame,
            "Register Doctor",
            command=self.register_doctor,
            fg_color=UI_COLORS['primary'],
            hover_color=UI_COLORS['hover'],
            width=200,
            height=40
        )
        register_btn.grid(row=0, column=0, padx=10)

        exit_btn = UIHelpers.create_styled_button(
            button_frame,
            "Exit",
            command=self.window.quit,
            fg_color=UI_COLORS['danger'],
            hover_color="#C0392B",
            width=100,
            height=40
        )
        exit_btn.grid(row=0, column=1, padx=10)

    def register_doctor(self):
        # Get form data
        data = {}
        for field_name, entry in self.entries.items():
            if hasattr(entry, 'get'):
                data[field_name] = entry.get().strip()
            else:
                data[field_name] = ""

        # Validate required fields
        required_fields = {
            "Clinic Name": data['clinic_name'],
            "Doctor Name": data['doctor_name'],
            "Email": data['email'],
            "Phone": data['phone'],
            "Username": data['username'],
            "Password": data['password']
        }

        empty_fields = ValidationHelpers.validate_required_fields(**required_fields)
        if empty_fields:
            MessageHelpers.show_error("Validation Error", f"Please fill in all required fields: {', '.join(empty_fields)}",parent=self.window)
            return

        # Validate email
        if not ValidationHelpers.validate_email(data['email']):
            MessageHelpers.show_error("Validation Error", "Please enter a valid email address",parent=self.window)
            return

        # Validate phone
        if not ValidationHelpers.validate_phone(data['phone']):
            MessageHelpers.show_error("Validation Error", "Please enter a valid phone number",parent=self.window)
            return

        # Validate password
        is_valid, message = ValidationHelpers.validate_password(data['password'])
        if not is_valid:
            MessageHelpers.show_error("Validation Error", message,parent=self.window)
            return

        # Register doctor
        success, message = self.doctor_model.register_doctor(
            data['clinic_name'],
            data['doctor_name'],
            data['specialization'],
            data['email'],
            data['phone'],
            data['username'],
            data['password']
        )

        if success:
            MessageHelpers.show_success("Success", "Doctor registered successfully! You can now login.",parent=self.window)
            self.window.destroy()
            if self.on_complete_callback:
                self.on_complete_callback()
        else:
            MessageHelpers.show_error("Registration Error", message,parent=self.window)

    def destroy(self):
        self.window.destroy()
