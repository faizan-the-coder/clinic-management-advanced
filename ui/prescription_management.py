import customtkinter as ctk
from database.models import PrescriptionModel, PatientModel, MedicineModel
from utils.helpers import UIHelpers, MessageHelpers
from utils.pdf_generator import PDFGenerator
from config import UI_COLORS
from datetime import date
import os


class PrescriptionManagementWindow:
    def __init__(self, doctor_info):
        self.doctor_info = doctor_info
        self.prescription_model = PrescriptionModel()
        self.patient_model = PatientModel()
        self.medicine_model = MedicineModel()
        self.prescription_items = []
        self.current_prescription_id = None
        self.editing_index = None

        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("Prescription Management")
        self.window.geometry("1200x680+10+0")
        self.window.transient()
        self.window.grab_set()

        self.setup_ui()
        self.load_patients()
        self.load_medicines()

    def setup_ui(self):
        # Main container divided into two columns
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=2)  # Entry panel weight
        main_frame.grid_columnconfigure(1, weight=3)  # Preview panel weight
        main_frame.grid_rowconfigure(0, weight=1)

        # Entry/Edit Panel (Left)
        self.entry_frame = UIHelpers.create_rounded_frame(
            main_frame, fg_color=UI_COLORS['card'], corner_radius=15
        )
        self.entry_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        self.entry_frame.grid_columnconfigure((0, 1), weight=1)
        self.entry_frame.grid_rowconfigure(1, weight=1)

        self.setup_patient_section(self.entry_frame)
        self.setup_medicine_section(self.entry_frame)
        self.setup_action_buttons(self.entry_frame)

        # Preview/History Panel (Right)
        self.preview_frame = UIHelpers.create_rounded_frame(
            main_frame, fg_color=UI_COLORS['background'], corner_radius=15
        )
        self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=0)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)

        self.setup_prescription_preview(self.preview_frame)  # <-- new method below

    def setup_prescription_preview(self, parent):
        # Title
        preview_label = UIHelpers.create_subtitle_label(
            parent, "Prescription History & Preview", text_color=UI_COLORS['primary']
        )
        preview_label.pack(pady=(10, 6))

        # Search frame
        search_frame = ctk.CTkFrame(parent, fg_color=UI_COLORS['background'])
        search_frame.pack(fill="x", pady=(10, 5), padx=10)

        # Add label describing what to search
        search_label = UIHelpers.create_normal_label(
            search_frame, "Search by patient name or diagnosis:", text_color=UI_COLORS['text']
        )
        search_label.pack(side="top", anchor="w", pady=(0, 3))

        # Entry for real-time search
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var
        )
        search_entry.pack(side="top", fill="x", expand=True)

        # Bind variable change for real-time search
        self.search_var.trace_add('write', lambda *args: self.perform_search())

        # Prescription list container
        self.prescription_listbox = ctk.CTkScrollableFrame(parent, fg_color=UI_COLORS['background'])
        self.prescription_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.load_prescription_history()

    def perform_search(self):
        search_text = self.search_var.get().strip()
        if not search_text:
            self.load_prescription_history()
            return

        # Filter prescriptions by calling model method
        results = self.prescription_model.search_prescriptions(search_text)
        self.display_prescriptions(results)

    def load_prescription_history(self):
        prescriptions = self.prescription_model.get_all_prescriptions()
        self.display_prescriptions(prescriptions)

    def display_prescriptions(self, prescriptions):
        # Clear existing widgets in the prescription list container
        for widget in self.prescription_listbox.winfo_children():
            widget.destroy()

        try:
            for presc in prescriptions:
                card = UIHelpers.create_rounded_frame(
                    self.prescription_listbox, fg_color=UI_COLORS['card'], corner_radius=10, height=70
                )
                card.pack(fill="x", padx=3, pady=5)

                # Make grid flexible: column 0 expands, column 1+ are fixed
                card.grid_columnconfigure(0, weight=1)

                # Title: Patient Name and Date
                title = f"{presc['patient_name']} ({presc['prescription_date']})"
                lbl_title = UIHelpers.create_subtitle_label(
                    card, title, text_color=UI_COLORS['primary']
                )
                lbl_title.grid(row=0, column=0, sticky="w", padx=12, pady=(6, 0))

                # Diagnosis label
                diagnosis = presc.get('diagnosis', '')
                lbl_diag = UIHelpers.create_normal_label(
                    card, f"Diagnosis: {diagnosis}", text_color=UI_COLORS['text']
                )
                lbl_diag.grid(row=1, column=0, sticky="w", padx=12, pady=(2, 8))

                # View button (👁 Eye)
                view_btn = UIHelpers.create_styled_button(
                    card, "👁",
                    command=lambda pid=presc['prescription_id']: self.load_prescription(pid),
                    fg_color=UI_COLORS['secondary'],
                    hover_color="#8B2E5B",
                    width=40
                )
                view_btn.grid(row=0, column=1, rowspan=2, padx=6, pady=6, sticky="e")

                # Delete button (🗑 Trash)
                delete_btn = UIHelpers.create_styled_button(
                    card, "🗑",
                    command=self.delete_prescription,
                    fg_color="#F44336",
                    hover_color="#D32F2F",
                    width=40
                )
                delete_btn.grid(row=0, column=2, rowspan=2, padx=6, pady=6, sticky="e")

        except Exception as e:
            MessageHelpers.show_error("Error", f"Unable to display prescriptions: {str(e)}",parent=self.window)

    def load_prescription(self, prescription_id):
        # Clear current form and prescription items
        self.current_prescription_id = prescription_id

        self.clear_form()
        self.save_btn.configure(text="Update Prescription")

        # Fetch prescription details and items from the model
        prescription, items = self.prescription_model.get_prescription_by_id(prescription_id)
        if not prescription:
            MessageHelpers.show_error("Not Found", f"No prescription found for ID {prescription_id}",parent=self.window)
            return

        # Set patient selection (assuming patient_combo stores options as 'id - name')
        patient_id = str(prescription['patient_id'])
        patient_options = self.patient_combo.cget('values')
        for option in patient_options:
            if option.startswith(patient_id + ' ') or option.startswith(patient_id + ' -'):
                self.patient_combo.set(option)
                break

        # Fill diagnosis
        self.diagnosis_entry.delete(0, "end")
        self.diagnosis_entry.insert(0, prescription.get('diagnosis', ''))

        # Load prescribed medicines
        self.prescription_items.clear()
        for item in items:
            self.prescription_items.append({
                'medicine': item.get('medicine_name', ''),
                'dosage': item.get('dosage', ''),
                'duration': item.get('duration', ''),
                'remarks': item.get('remarks', ''),
            })

        self.update_medicine_display()
        # Optionally highlight the preview or bring focus to the loaded card

    def setup_patient_section(self, parent):
        # Patient selection frame
        patient_frame = ctk.CTkFrame(parent, fg_color="transparent")
        patient_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        patient_frame.grid_columnconfigure((1, 3), weight=1)

        # Patient
        UIHelpers.create_normal_label(patient_frame, "Patient*:", text_color=UI_COLORS['text']).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )

        self.patient_combo = UIHelpers.create_styled_combobox(
            patient_frame, values=[], width=250
        )
        self.patient_combo.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=5)
        self.patient_combo.set('Select patient')

        # Diagnosis
        UIHelpers.create_normal_label(patient_frame, "Diagnosis:", text_color=UI_COLORS['text']).grid(
            row=0, column=2, sticky="w", padx=(0, 10), pady=5
        )

        self.diagnosis_entry = UIHelpers.create_styled_entry(
            patient_frame, placeholder_text="Enter diagnosis", width=250
        )
        self.diagnosis_entry.grid(row=0, column=3, sticky="w", pady=5)

    def setup_medicine_section(self, parent):
        # Medicine section
        med_frame = ctk.CTkFrame(parent, fg_color="transparent")
        med_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
        med_frame.grid_columnconfigure(0, weight=1)
        med_frame.grid_rowconfigure(1, weight=1)

        # Medicine entry form
        entry_frame = UIHelpers.create_rounded_frame(
            med_frame,
            fg_color=UI_COLORS['background'],
            corner_radius=10
        )
        entry_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        entry_frame.grid_columnconfigure((1, 2, 3, 4), weight=1)

        # Medicine form fields
        UIHelpers.create_normal_label(entry_frame, "Medicine:", text_color=UI_COLORS['text']).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.medicine_combo = UIHelpers.create_styled_combobox(entry_frame, values=[], width=150)
        self.medicine_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.medicine_combo.set('Select Medicine')

        UIHelpers.create_normal_label(entry_frame, "Dosage:", text_color=UI_COLORS['text']).grid(
            row=0, column=2, padx=10, pady=10, sticky="w"
        )
        self.dosage_entry = UIHelpers.create_styled_entry(entry_frame, placeholder_text="e.g., 1 tablet", width=100)
        self.dosage_entry.grid(row=0, column=3, padx=5, pady=10, sticky="ew")

        UIHelpers.create_normal_label(entry_frame, "Duration:", text_color=UI_COLORS['text']).grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.duration_combo = UIHelpers.create_styled_combobox(
            entry_frame,
            values=["3 days", "5 days", "7 days", "10 days", "15 days", "1 month"],
            width=100
        )
        self.duration_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.duration_combo.set('Select Duration')

        UIHelpers.create_normal_label(entry_frame, "Remarks:", text_color=UI_COLORS['text']).grid(
            row=1, column=2, padx=10, pady=5, sticky="w"
        )
        self.remarks_entry = UIHelpers.create_styled_entry(entry_frame, placeholder_text="After meals", width=150)
        self.remarks_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.add_med_btn = UIHelpers.create_styled_button(
            entry_frame,
            "Add Medicine",
            command=self.add_medicine,
            fg_color=UI_COLORS['secondary'],
            hover_color="#8B2E5B",
            width=120
        )
        self.add_med_btn.grid(row=0, column=4, rowspan=2, padx=10, pady=10)

        # Medicine list
        UIHelpers.create_subtitle_label(
            med_frame, "Prescribed Medicines:", text_color=UI_COLORS['primary']
        ).grid(row=1, column=0, sticky="w", pady=(10, 5))

        self.medicine_listbox = ctk.CTkScrollableFrame(
            med_frame,
            fg_color=UI_COLORS['background']
        )
        self.medicine_listbox.grid(row=2, column=0, sticky="nsew")

    def setup_action_buttons(self, parent):
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        self.save_btn = UIHelpers.create_styled_button(
            button_frame,
            "Save Prescription",
            command=self.handle_save_update,
            fg_color=UI_COLORS['primary'],
            hover_color=UI_COLORS['hover'],
            width=150
        )
        self.save_btn.grid(row=0, column=0, padx=10)

        pdf_btn = UIHelpers.create_styled_button(
            button_frame,
            "Generate PDF",
            command=self.generate_pdf,
            fg_color=UI_COLORS['success'],
            hover_color="#D68910",
            width=120
        )
        pdf_btn.grid(row=0, column=3, padx=10)

        clear_btn = UIHelpers.create_styled_button(
            button_frame,
            "Clear All",
            command=self.clear_form,
            fg_color=UI_COLORS['text_secondary'],
            hover_color="#555555",
            width=100
        )
        clear_btn.grid(row=0, column=4, padx=10)

    def load_patients(self):
        try:
            patients = self.patient_model.get_all_patients()
            patient_options = [f"{p['patient_id']} - {p['name']}" for p in patients]
            self.patient_combo.configure(values=patient_options)
        except Exception as e:
            print(f"Error loading patients: {e}")

    def load_medicines(self):
        try:
            medicines = self.medicine_model.get_all_medicines()
            medicine_options = [med['name'] for med in medicines]
            self.medicine_combo.configure(values=medicine_options)
        except Exception as e:
            print(f"Error loading medicines: {e}")

    def add_medicine(self):
        medicine = self.medicine_combo.get()
        dosage = self.dosage_entry.get()
        duration = self.duration_combo.get()
        remarks = self.remarks_entry.get()

        if not medicine or medicine == "Select Medicine" or not dosage or not duration or duration == "Select Duration":
            MessageHelpers.show_error("Validation Error", "Please fill in medicine, dosage, and duration",parent=self.window)
            return

        item = {
            'medicine': medicine,
            'dosage': dosage,
            'duration': duration,
            'remarks': remarks
        }

        if self.editing_index is not None:
            # Replace existing medicine instead of appending
            self.prescription_items[self.editing_index] = item
            self.editing_index = None
            self.add_med_btn.configure(text="Add Medicine")  # toggle back
        else:
            self.prescription_items.append(item)

        # Reset form fields with placeholders
        self.medicine_combo.set("Select Medicine")
        self.dosage_entry.delete(0, 'end')
        self.dosage_entry.configure(placeholder_text="e.g., 1 tablet")
        self.duration_combo.set("Select Duration")
        self.remarks_entry.delete(0, 'end')
        self.remarks_entry.configure(placeholder_text="After meals")

        self.update_medicine_display()

    def update_medicine_display(self):
        # Clear existing items
        for widget in self.medicine_listbox.winfo_children():
            widget.destroy()

        # Display items
        for i, item in enumerate(self.prescription_items):
            item_frame = UIHelpers.create_rounded_frame(
                self.medicine_listbox,
                fg_color=UI_COLORS['card'],
                corner_radius=8,
                height=60
            )
            item_frame.pack(fill="x", pady=2)
            item_frame.grid_columnconfigure(1, weight=1)
            item_frame.grid_propagate(False)

            # Medicine name
            med_label = UIHelpers.create_normal_label(
                item_frame,
                item['medicine'],
                text_color=UI_COLORS['primary']
            )
            med_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Details
            details = f"{item['dosage']} - {item['duration']}"
            if item['remarks']:
                details += f" ({item['remarks']})"

            details_label = UIHelpers.create_normal_label(
                item_frame,
                details,
                text_color=UI_COLORS['text']
            )
            details_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            # Edit button (✏️)
            edit_btn = UIHelpers.create_styled_button(
                item_frame,
                "🖊",
                command=lambda idx=i: self.edit_medicine(idx),
                fg_color="#3498DB",  # Blue
                hover_color="#2980B9",
                width=30,
                height=25
            )
            edit_btn.grid(row=0, column=2, padx=5, pady=5)

            # Remove button (×)
            remove_btn = UIHelpers.create_styled_button(
                item_frame,
                "×",
                command=lambda idx=i: self.remove_medicine(idx),
                fg_color=UI_COLORS['danger'],
                hover_color="#C0392B",
                width=30,
                height=25
            )
            remove_btn.grid(row=0, column=3, padx=5, pady=5)

    def remove_medicine(self, index):
        if 0 <= index < len(self.prescription_items):
            self.prescription_items.pop(index)
            self.update_medicine_display()

    def edit_medicine(self, index):
        if 0 <= index < len(self.prescription_items):
            item = self.prescription_items[index]
            self.editing_index = index

            # Fill fields with existing medicine details
            self.medicine_combo.set(item['medicine'])
            self.dosage_entry.delete(0, 'end')
            self.dosage_entry.insert(0, item['dosage'])
            self.duration_combo.set(item['duration'])
            self.remarks_entry.delete(0, 'end')
            self.remarks_entry.insert(0, item['remarks'])

            # Change button text to "Update Medicine"
            self.add_med_btn.configure(text="Update Medicine")

    def handle_save_update(self):
        if self.current_prescription_id:
            self.update_prescription()
        else:
            self.save_prescription()

    def save_prescription(self):
        if not self.patient_combo.get():
            MessageHelpers.show_error("Validation Error", "Please select a patient",parent=self.window)
            return

        if not self.prescription_items:
            MessageHelpers.show_error("Validation Error", "Please add at least one medicine",parent=self.window)
            return

        try:
            # Extract patient ID
            patient_id = self.patient_combo.get().split(' - ')[0]
            diagnosis = self.diagnosis_entry.get()

            # Save prescription
            success, prescription_id = self.prescription_model.create_prescription(
                patient_id, diagnosis, self.prescription_items
            )

            if success:
                MessageHelpers.show_success("Success", f"Prescription saved successfully! ID: {prescription_id}",parent=self.window)
                self.clear_form()
                self.load_prescription_history()
            else:
                MessageHelpers.show_error("Error", prescription_id,parent=self.window)  # Contains error message

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to save prescription: {str(e)}",parent=self.window)

    def generate_pdf(self):
        if not self.patient_combo.get():
            MessageHelpers.show_error("Error", "Please select a patient",parent=self.window)
            return

        if not self.prescription_items:
            MessageHelpers.show_error("Error", "Please add medicines to prescription",parent=self.window)
            return

        try:
            # Get patient info
            patient_id = self.patient_combo.get().split(' - ')[0]
            patient = self.patient_model.get_patient_by_id(patient_id)

            if not patient:
                MessageHelpers.show_error("Error", "Patient not found",parent=self.window)
                return

            # Create PDF
            pdf_generator = PDFGenerator(
                self.doctor_info['clinic_name'],
                self.doctor_info['doctor_name']
            )

            # Prepare prescription data
            prescription_data = {
                'prescription_date': date.today().strftime('%Y-%m-%d'),
                'diagnosis': self.diagnosis_entry.get()
            }

            # Create downloads directory if it doesn't exist
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            filename = f"{downloads_dir}/prescription_{patient_id}_{date.today().strftime('%Y%m%d')}.pdf"

            success, message = pdf_generator.generate_prescription(
                patient, prescription_data, self.prescription_items, filename
            )

            if success:
                MessageHelpers.show_success("Success", f"PDF generated successfully!\nSaved as: {filename}",parent=self.window)
            else:
                MessageHelpers.show_error("Error", message,parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate PDF: {str(e)}",parent=self.window)

    def clear_form(self):
        # Reset patient selection
        self.patient_combo.set("Select Patient")

        self.diagnosis_entry.delete(0, 'end')
        self.diagnosis_entry.configure(placeholder_text="Enter diagnosis")

        self.medicine_combo.set("Select Medicine")
        self.dosage_entry.delete(0, 'end')
        self.dosage_entry.configure(placeholder_text="e.g., 1 tablet")

        self.duration_combo.set("Select Duration")
        self.remarks_entry.delete(0, 'end')
        self.remarks_entry.configure(placeholder_text="After meals")

        self.prescription_items.clear()
        self.update_medicine_display()

        # Button text reset only if no prescription loaded
        if not self.current_prescription_id:
            self.save_btn.configure(text="Save Prescription")

    def update_prescription(self):
        if not self.current_prescription_id:
            MessageHelpers.show_error("Error", "Load a prescription before updating.",parent=self.window)
            return

        # Validate required fields as needed
        patient_str = self.patient_combo.get()
        if not patient_str:
            MessageHelpers.show_warning("Warning", "Please select a patient.",parent=self.window)
            return

        patient_id = patient_str.split(' ')[0]  # Assuming ID is before first space

        diagnosis = self.diagnosis_entry.get().strip()

        # Validate prescription items list
        if not self.prescription_items:
            MessageHelpers.show_warning("Warning", "Add at least one medicine before updating.",parent=self.window)
            return

        # Update main prescription record
        success, msg = self.prescription_model.update_prescription(
            self.current_prescription_id, patient_id, diagnosis
        )

        if not success:
            MessageHelpers.show_error("Error", f"Failed to update prescription: {msg}",parent=self.window)
            return

        # Update prescription items - remove existing then insert updated
        self.prescription_model.delete_prescription_items(self.current_prescription_id)

        for item in self.prescription_items:
            self.prescription_model.add_prescription_item(
                self.current_prescription_id,
                item['medicine'],
                item['dosage'],
                item['duration'],
                item['remarks']
            )

        MessageHelpers.show_success("Success", "Prescription updated successfully.",parent=self.window)
        self.load_prescription_history()

    def delete_prescription(self):
        if not self.current_prescription_id:
            MessageHelpers.show_error("Error", "Load a prescription before deleting.",parent=self.window)
            return

        confirm = MessageHelpers.ask_confirmation(
            "Confirm Delete",
            "Are you sure you want to delete this prescription? This action cannot be undone.",parent=self.window
        )
        if not confirm:
            return

        success = self.prescription_model.delete_prescription(self.current_prescription_id)
        if success:
            MessageHelpers.show_success("Deleted", "Prescription successfully deleted.",parent=self.window)
            self.clear_form()
            self.load_prescription_history()
        else:
            MessageHelpers.show_error("Error", "Failed to delete prescription.",parent=self.window)
