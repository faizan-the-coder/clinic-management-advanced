import customtkinter as ctk
from database.models import PatientModel
from utils.helpers import UIHelpers, ValidationHelpers, MessageHelpers, DateHelpers
from config import UI_COLORS
from tkcalendar import DateEntry
from datetime import date


class PatientManagementWindow:
    def __init__(self, doctor_info):
        self.doctor_info = doctor_info
        self.patient_model = PatientModel()
        self.current_patient = None


        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("Patient Management")
        self.window.geometry("1000x680+10+0")
        self.window.transient()
        self.window.grab_set()

        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.load_patients()

    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Left panel - Patient list
        self.setup_patient_list(main_frame)

        # Right panel - Patient form
        self.setup_patient_form(main_frame)

    def setup_patient_list(self, parent):
        # Patient list frame
        list_frame = UIHelpers.create_rounded_frame(
            parent,
            fg_color=UI_COLORS['card'],
            corner_radius=15,
            width=400
        )
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(2, weight=1)
        list_frame.grid_propagate(False)

        # Header
        header_label = UIHelpers.create_subtitle_label(
            list_frame,
            "Patient List",
            text_color=UI_COLORS['primary']
        )
        header_label.grid(row=0, column=0, pady=15, sticky="w", padx=20)

        # Search frame
        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = UIHelpers.create_styled_entry(
            search_frame,
            placeholder_text="Search patients...",
            width=300
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)

        search_btn = UIHelpers.create_styled_button(
            search_frame,
            "🔍",
            command=self.search_patients,
            width=40,
            height=35
        )
        search_btn.grid(row=0, column=1)

        # Patient list
        self.patient_listbox = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=UI_COLORS['background']
        )
        self.patient_listbox.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=(0, 20))

        new_btn = UIHelpers.create_styled_button(
            button_frame,
            "New Patient",
            command=self.clear_form,
            fg_color=UI_COLORS['primary'],
            hover_color=UI_COLORS['hover'],
            width=120
        )
        new_btn.grid(row=0, column=0, padx=5)

        delete_btn = UIHelpers.create_styled_button(
            button_frame,
            "Delete",
            command=self.delete_patient,
            fg_color=UI_COLORS['danger'],
            hover_color="#C0392B",
            width=80
        )
        delete_btn.grid(row=0, column=1, padx=5)

    def setup_patient_form(self, parent):
        # Patient form frame
        form_frame = UIHelpers.create_rounded_frame(
            parent,
            fg_color=UI_COLORS['card'],
            corner_radius=15
        )
        form_frame.grid(row=0, column=1, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)

        # Header
        form_header = UIHelpers.create_subtitle_label(
            form_frame,
            "Patient Information",
            text_color=UI_COLORS['primary']
        )
        form_header.grid(row=0, column=0, columnspan=2, pady=15, sticky="w", padx=20)

        # Form fields
        self.setup_form_fields(form_frame)

        # Action buttons
        self.setup_form_buttons(form_frame)

    def setup_form_fields(self, parent):
        # Patient ID (read-only)
        UIHelpers.create_normal_label(parent, "Patient ID:", text_color=UI_COLORS['text']).grid(
            row=1, column=0, sticky="w", padx=20, pady=5
        )
        self.patient_id_label = UIHelpers.create_normal_label(
            parent, "Auto-generated", text_color=UI_COLORS['text_secondary']
        )
        self.patient_id_label.grid(row=1, column=1, sticky="w", padx=20, pady=5)

        # Name
        UIHelpers.create_normal_label(parent, "Name*:", text_color=UI_COLORS['text']).grid(
            row=2, column=0, sticky="w", padx=20, pady=5
        )
        self.name_entry = UIHelpers.create_styled_entry(parent, placeholder_text="Enter patient name", width=300)
        self.name_entry.grid(row=2, column=1, sticky="w", padx=20, pady=5)

        # Gender
        UIHelpers.create_normal_label(parent, "Gender*:", text_color=UI_COLORS['text']).grid(
            row=3, column=0, sticky="w", padx=20, pady=5
        )
        self.gender_combo = UIHelpers.create_styled_combobox(
            parent, values=["Male", "Female", "Other"], width=150
        )
        self.gender_combo.grid(row=3, column=1, sticky="w", padx=20, pady=5)

        # Date of Birth
        UIHelpers.create_normal_label(parent, "Date of Birth*:", text_color=UI_COLORS['text']).grid(
            row=4, column=0, sticky="w", padx=20, pady=5
        )

        # Create a frame for DOB and Age
        dob_frame = ctk.CTkFrame(parent, fg_color="transparent")
        dob_frame.grid(row=4, column=1, sticky="w", padx=20, pady=5)

        self.dob_entry = DateEntry(
            dob_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            maxdate=date.today()
        )
        self.dob_entry.pack(side="left")
        self.dob_entry.bind('<<DateEntrySelected>>', self.calculate_age)

        # Age (auto-calculated)
        age_label = UIHelpers.create_normal_label(dob_frame, "Age:", text_color=UI_COLORS['text'])
        age_label.pack(side="left", padx=(20, 5))

        self.age_label = UIHelpers.create_normal_label(dob_frame, "0", text_color=UI_COLORS['text_secondary'])
        self.age_label.pack(side="left")

        # Phone
        UIHelpers.create_normal_label(parent, "Phone:", text_color=UI_COLORS['text']).grid(
            row=5, column=0, sticky="w", padx=20, pady=5
        )
        self.phone_entry = UIHelpers.create_styled_entry(parent, placeholder_text="Enter phone number", width=200)
        self.phone_entry.grid(row=5, column=1, sticky="w", padx=20, pady=5)

        # Email
        UIHelpers.create_normal_label(parent, "Email:", text_color=UI_COLORS['text']).grid(
            row=6, column=0, sticky="w", padx=20, pady=5
        )
        self.email_entry = UIHelpers.create_styled_entry(parent, placeholder_text="Enter email address", width=300)
        self.email_entry.grid(row=6, column=1, sticky="w", padx=20, pady=5)

        # Address
        UIHelpers.create_normal_label(parent, "Address:", text_color=UI_COLORS['text']).grid(
            row=7, column=0, sticky="nw", padx=20, pady=5
        )
        self.address_textbox = UIHelpers.create_styled_textbox(parent, height=60, width=300)
        self.address_textbox.grid(row=7, column=1, sticky="w", padx=20, pady=5)

        # Medical History
        UIHelpers.create_normal_label(parent, "Medical History:", text_color=UI_COLORS['text']).grid(
            row=8, column=0, sticky="nw", padx=20, pady=5
        )
        self.medical_history_textbox = UIHelpers.create_styled_textbox(parent, height=60, width=300)
        self.medical_history_textbox.grid(row=8, column=1, sticky="w", padx=20, pady=5)

        # Allergies
        UIHelpers.create_normal_label(parent, "Allergies:", text_color=UI_COLORS['text']).grid(
            row=9, column=0, sticky="nw", padx=20, pady=5
        )
        self.allergies_textbox = UIHelpers.create_styled_textbox(parent, height=60, width=300)
        self.allergies_textbox.grid(row=9, column=1, sticky="w", padx=20, pady=5)


    def setup_form_buttons(self, parent):
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=11, column=0, columnspan=2, pady=20)

        self.save_btn = UIHelpers.create_styled_button(
            button_frame,
            "Save Patient",
            command=self.save_patient,
            fg_color=UI_COLORS['primary'],
            hover_color=UI_COLORS['hover'],
            width=150
        )
        self.save_btn.grid(row=0, column=0, padx=10)

        self.update_btn = UIHelpers.create_styled_button(
            button_frame,
            "Update Patient",
            command=self.update_patient,
            fg_color=UI_COLORS['success'],
            hover_color="#D68910",
            width=150
        )
        self.update_btn.grid(row=0, column=1, padx=10)
        self.update_btn.grid_remove()  # Hide initially

        close_btn = UIHelpers.create_styled_button(
            button_frame,
            "Close",
            command=self.window.destroy,
            fg_color=UI_COLORS['danger'],
            hover_color="#C0392B",
            width=100
        )
        close_btn.grid(row=0, column=2, padx=10)

    def calculate_age(self, event=None):
        try:
            dob = self.dob_entry.get_date()
            age = DateHelpers.calculate_age(dob)
            self.age_label.configure(text=str(age))
        except:
            self.age_label.configure(text="0")



    def load_patients(self):
        try:
            patients = self.patient_model.get_all_patients()
            self.display_patients(patients)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to load patients: {str(e)}",parent=self.window)

    def display_patients(self, patients):
        # Clear existing patients
        for widget in self.patient_listbox.winfo_children():
            widget.destroy()

        if not patients:
            no_patients_label = UIHelpers.create_normal_label(
                self.patient_listbox,
                "No patients found",
                text_color=UI_COLORS['text_secondary']
            )
            no_patients_label.pack(pady=20)
            return

        # Display patients
        for patient in patients:
            patient_frame = UIHelpers.create_rounded_frame(
                self.patient_listbox,
                fg_color=UI_COLORS['card'],
                corner_radius=8,
                height=60
            )
            patient_frame.pack(fill="x", pady=2)
            patient_frame.grid_columnconfigure(1, weight=1)
            patient_frame.grid_propagate(False)

            # Patient ID
            id_label = UIHelpers.create_normal_label(
                patient_frame,
                patient['patient_id'],
                text_color=UI_COLORS['primary']
            )
            id_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Patient Name
            name_label = UIHelpers.create_normal_label(
                patient_frame,
                patient['name'],
                text_color=UI_COLORS['text']
            )
            name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            # Age/Gender
            age_gender = f"{patient['age']}Y, {patient['gender']}"
            age_label = UIHelpers.create_normal_label(
                patient_frame,
                age_gender,
                text_color=UI_COLORS['text_secondary']
            )
            age_label.grid(row=1, column=1, padx=10, pady=(0, 5), sticky="w")

            # Phone
            phone_label = UIHelpers.create_normal_label(
                patient_frame,
                patient['phone'] or "No phone",
                text_color=UI_COLORS['text_secondary']
            )
            phone_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

            # Make clickable
            for widget in [patient_frame, id_label, name_label, age_label, phone_label]:
                widget.bind("<Button-1>", lambda e, p=patient: self.select_patient(p))
                widget.configure(cursor="hand2")

    def select_patient(self, patient):
        self.current_patient = patient


        self.populate_form(patient)

    def populate_form(self, patient):
        # Clear form first
        self.clear_form()

        # Populate fields
        self.patient_id_label.configure(text=patient['patient_id'])
        self.name_entry.insert(0, patient['name'])
        self.gender_combo.set(patient['gender'])

        # Set DOB
        try:
            if isinstance(patient['dob'], str):
                dob = DateHelpers.string_to_date(patient['dob'])
            else:
                dob = patient['dob']
            self.dob_entry.set_date(dob)
            self.calculate_age()
        except:
            pass

        if patient['phone']:
            self.phone_entry.insert(0, patient['phone'])
        if patient['email']:
            self.email_entry.insert(0, patient['email'])
        if patient['address']:
            self.address_textbox.insert("1.0", patient['address'])
        if patient['medical_history']:
            self.medical_history_textbox.insert("1.0", patient['medical_history'])
        if patient['allergies']:
            self.allergies_textbox.insert("1.0", patient['allergies'])

        # Show update button, hide save button
        self.save_btn.grid_remove()
        self.update_btn.grid()

    def clear_form(self):
        self.patient_id_label.configure(text="Auto-generated")

        self.name_entry.delete(0, 'end')
        self.name_entry.configure(placeholder_text="Enter patient name")

        self.gender_combo.set("Male")
        self.dob_entry.set_date(date.today())
        self.age_label.configure(text="0")

        self.phone_entry.delete(0, 'end')
        self.phone_entry.configure(placeholder_text="Enter phone number")

        self.email_entry.delete(0, 'end')
        self.email_entry.configure(placeholder_text="Enter email address")

        self.address_textbox.delete("1.0", 'end')
        self.medical_history_textbox.delete("1.0", 'end')
        self.allergies_textbox.delete("1.0", 'end')

        # Show save button, hide update button
        self.update_btn.grid_remove()
        self.save_btn.grid()




    def delete_patient(self):
        if not self.current_patient:
            MessageHelpers.show_warning("No Selection", "Please select a patient to delete",parent=self.window)
            return
        confirmed = MessageHelpers.ask_confirmation("Confirm Deletion",
                                                    f"Delete patient {self.current_patient['name']}?",parent=self.window)
        if confirmed:
            success, msg = self.patient_model.delete_patient(self.current_patient['patient_id'])
            if success:
                MessageHelpers.show_success('success',"Patient deleted successfully.",parent=self.window)
                self.current_patient = None
                self.load_patients()
                self.clear_form()
            else:
                MessageHelpers.show_success(f"Failed to delete patient: {msg}",parent=self.window)

    def validate_form(self):
        # Get form data
        name = self.name_entry.get().strip()
        gender = self.gender_combo.get().strip()

        # Validate required fields
        if not name:
            MessageHelpers.show_error("Validation Error", "Patient name is required",parent=self.window)
            return False

        if not gender:
            MessageHelpers.show_error("Validation Error", "Please select gender",parent=self.window)
            return False

        # Validate email if provided
        email = self.email_entry.get().strip()
        if email and not ValidationHelpers.validate_email(email):
            MessageHelpers.show_error("Validation Error", "Please enter a valid email address",parent=self.window)
            return False

        # Validate phone if provided
        phone = self.phone_entry.get().strip()
        if phone and not ValidationHelpers.validate_phone(phone):
            MessageHelpers.show_error("Validation Error", "Please enter a valid phone number",parent=self.window)
            return False

        return True

    def get_form_data(self):
        return {
            'name': self.name_entry.get().strip(),
            'gender': self.gender_combo.get().strip(),
            'dob': self.dob_entry.get_date(),
            'phone': self.phone_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'address': self.address_textbox.get("1.0", 'end').strip(),
            'medical_history': self.medical_history_textbox.get("1.0", 'end').strip(),
            'allergies': self.allergies_textbox.get("1.0", 'end').strip(),

        }

    def save_patient(self):
        if not self.validate_form():
            return

        data = self.get_form_data()

        try:
            success, patient_id = self.patient_model.add_patient(
                data['name'], data['gender'], data['dob'],
                data['address'], data['phone'], data['email'],
                data['medical_history'], data['allergies']
            )

            if success:
                MessageHelpers.show_success("Success", f"Patient added successfully! Patient ID: {patient_id}",parent=self.window)
                self.clear_form()
                self.load_patients()
            else:
                MessageHelpers.show_error("Error", patient_id,parent=self.window)  # patient_id contains error message

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to save patient: {str(e)}",parent=self.window)

    def update_patient(self):
        if not self.current_patient:
            MessageHelpers.show_warning("No Selection", "Please select a patient to update",parent=self.window)
            return

        if not self.validate_form():
            return

        data = self.get_form_data()

        try:
            success, message = self.patient_model.update_patient(
                self.current_patient['patient_id'],
                data['name'], data['gender'], data['dob'],
                data['address'], data['phone'], data['email'],
                data['medical_history'], data['allergies']
            )

            if success:
                MessageHelpers.show_success("Success", "Patient updated successfully!",parent=self.window)
                self.load_patients()
            else:
                MessageHelpers.show_error("Error", message,parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to update patient: {str(e)}",parent=self.window)

    def on_search(self, event=None):
        # Simple search as user types
        search_term = self.search_entry.get().strip()
        if len(search_term) >= 2:  # Search after 2 characters
            self.search_patients()
        elif len(search_term) == 0:  # Show all if search is cleared
            self.load_patients()

    def search_patients(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_patients()
            return

        try:
            patients = self.patient_model.search_patients(search_term)
            self.display_patients(patients)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Search failed: {str(e)}",parent=self.window)
