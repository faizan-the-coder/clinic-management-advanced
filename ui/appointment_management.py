import customtkinter as ctk
from database.models import AppointmentModel, PatientModel
from utils.helpers import UIHelpers, MessageHelpers, DateHelpers
from config import UI_COLORS
from tkcalendar import DateEntry
from datetime import date, datetime
import datetime

class AppointmentManagementWindow:
    def __init__(self, doctor_info):
        self.doctor_info = doctor_info
        self.appointment_model = AppointmentModel()
        self.patient_model = PatientModel()
        self.current_appointment = None

        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("Appointment Management")
        self.window.geometry("900x600+50+10")
        self.window.transient()
        self.window.grab_set()

        self.setup_ui()
        self.load_appointments()

    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Left panel - Appointment form
        self.setup_appointment_form(main_frame)
        self._on_date_change()

        # Right panel - Appointment list
        self.setup_appointment_list(main_frame)

    def _on_date_change(self, event=None):

        selected_date = self.date_entry.get_date()
        now = datetime.datetime.now()


        if selected_date == date.today():
            # If today, only show time slots from current hour and later (e.g., 3pm -> from 3:30pm onward)
            times = DateHelpers.get_time_slots()
            filtered_times = []
            current_hour = now.hour
            current_minute = now.minute
            for t in times:
                # Parse hour part from string, assuming format like '09:00', '15:30'
                hour, minute = map(int, t.split(':'))
                if hour > current_hour or (hour == current_hour and minute >= current_minute):
                    filtered_times.append(t)
            if not filtered_times:
                filtered_times = ["No slots available"]
            self.time_combo.configure(values=filtered_times)
            self.time_combo.set(filtered_times[0])
        else:
            # For future dates, show all slots
            times = DateHelpers.get_time_slots()
            self.time_combo.configure(values=times)
            self.time_combo.set(times[0])

    def setup_appointment_form(self, parent):
        # Form frame
        form_frame = UIHelpers.create_rounded_frame(
            parent,
            fg_color=UI_COLORS['card'],
            corner_radius=15,
            width=350
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_propagate(False)

        # Header
        header_label = UIHelpers.create_subtitle_label(
            form_frame,
            "Book Appointment",
            text_color=UI_COLORS['primary']
        )
        header_label.grid(row=0, column=0, columnspan=2, pady=15, sticky="w", padx=20)

        # Patient selection
        UIHelpers.create_normal_label(form_frame, "Patient*:", text_color=UI_COLORS['text']).grid(
            row=1, column=0, sticky="w", padx=20, pady=5
        )

        self.patient_combo = UIHelpers.create_styled_combobox(
            form_frame, values=[], width=250
        )
        self.patient_combo.grid(row=1, column=1, sticky="w", padx=20, pady=5)
        self.patient_combo.set("Select patient...")

        # Load patients
        self.load_patients()

        # Appointment Date
        UIHelpers.create_normal_label(form_frame, "Date*:", text_color=UI_COLORS['text']).grid(
            row=2, column=0, sticky="w", padx=20, pady=5
        )

        self.date_entry = DateEntry(
            form_frame,
            width=13,
            font=('arial',20),
            background='darkblue',
            foreground='white',
            borderwidth=6,
            date_pattern='yyyy-mm-dd',
            mindate=date.today()
        )
        self.date_entry.grid(row=2, column=1, sticky="w", padx=30, pady=5)

        self.date_entry.bind('<<DateEntrySelected>>', self._on_date_change)

        # Appointment Time
        UIHelpers.create_normal_label(form_frame, "Time*:", text_color=UI_COLORS['text']).grid(
            row=3, column=0, sticky="w", padx=20, pady=5
        )

        time_slots = DateHelpers.get_time_slots()
        self.time_combo = UIHelpers.create_styled_combobox(
            form_frame, values=time_slots, width=150
        )
        self.time_combo.grid(row=3, column=1, sticky="w", padx=20, pady=5)

        # Status
        UIHelpers.create_normal_label(form_frame, "Status:", text_color=UI_COLORS['text']).grid(
            row=4, column=0, sticky="w", padx=20, pady=5
        )

        self.status_combo = UIHelpers.create_styled_combobox(
            form_frame, values=["Scheduled", "Completed", "Cancelled"], width=150
        )
        self.status_combo.set("Scheduled")
        self.status_combo.grid(row=4, column=1, sticky="w", padx=20, pady=5)

        # Notes
        UIHelpers.create_normal_label(form_frame, "Notes:", text_color=UI_COLORS['text']).grid(
            row=5, column=0, sticky="nw", padx=20, pady=5
        )

        self.notes_textbox = UIHelpers.create_styled_textbox(form_frame, height=80, width=250)
        self.notes_textbox.grid(row=5, column=1, sticky="w", padx=20, pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        self.book_btn = UIHelpers.create_styled_button(
            button_frame,
            "Book Appointment",
            command=self.book_appointment,
            fg_color=UI_COLORS['primary'],
            hover_color=UI_COLORS['hover'],
            width=150
        )
        self.book_btn.grid(row=0, column=0, padx=5)

        self.update_btn = UIHelpers.create_styled_button(
            button_frame,
            "Update Status",
            command=self.update_appointment,
            fg_color=UI_COLORS['success'],
            hover_color="#D68910",
            width=100
        )
        self.update_btn.grid(row=0, column=1, padx=5)
        self.update_btn.grid_remove()

        clear_btn = UIHelpers.create_styled_button(
            button_frame,
            "Clear",
            command=self.clear_form,
            fg_color=UI_COLORS['text_secondary'],
            hover_color="#555555",
            width=80
        )
        clear_btn.grid(row=0, column=2, padx=5)

    def setup_appointment_list(self, parent):
        # List frame
        list_frame = UIHelpers.create_rounded_frame(
            parent,
            fg_color=UI_COLORS['card'],
            corner_radius=15
        )
        list_frame.grid(row=0, column=1, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(2, weight=1)

        # Header
        header_label = UIHelpers.create_subtitle_label(
            list_frame,
            "Appointments",
            text_color=UI_COLORS['primary']
        )
        header_label.grid(row=0, column=0, pady=15, sticky="w", padx=20)

        # Date filter
        filter_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))

        UIHelpers.create_normal_label(filter_frame, "View Date:", text_color=UI_COLORS['text']).pack(side="left")

        self.filter_date = DateEntry(
            filter_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.filter_date.pack(side="left", padx=(10, 0))
        self.filter_date.bind('<<DateEntrySelected>>', self.load_appointments)

        view_btn = UIHelpers.create_styled_button(
            filter_frame,
            "View",
            command=self.load_appointments,
            width=80,
            height=30
        )
        view_btn.pack(side="left", padx=(10, 0))

        # Appointments list
        self.appointments_listbox = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=UI_COLORS['background']
        )
        self.appointments_listbox.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

    def load_patients(self):
        try:
            patients = self.patient_model.get_all_patients()
            patient_options = [f"{p['patient_id']} - {p['name']}" for p in patients]
            self.patient_combo.configure(values=patient_options)
        except Exception as e:
            print(f"Error loading patients: {e}")

    def load_appointments(self, event=None):
        try:
            selected_date = self.filter_date.get_date()
            appointments = self.appointment_model.get_appointments_by_date(selected_date)

            self.display_appointments(appointments)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to load appointments: {str(e)}",parent=self.window)

    def display_appointments(self, appointments):
        # Clear existing appointments
        for widget in self.appointments_listbox.winfo_children():
            widget.destroy()

        if not appointments:
            no_apt_label = UIHelpers.create_normal_label(
                self.appointments_listbox,
                "No appointments found for selected date",
                text_color=UI_COLORS['text_secondary']
            )
            no_apt_label.pack(pady=20)
            return

        # Display appointments
        for apt in appointments:
            apt_frame = UIHelpers.create_rounded_frame(
                self.appointments_listbox,
                fg_color=UI_COLORS['card'],
                corner_radius=8,
                height=80
            )
            apt_frame.pack(fill="x", pady=2)
            apt_frame.grid_columnconfigure(1, weight=1)
            apt_frame.grid_propagate(False)



            appointment_time = apt['appointment_time']

            if isinstance(appointment_time, str):
                # Convert string to time
                try:
                    appointment_time_obj = datetime.datetime.strptime(appointment_time, '%H:%M:%S').time()
                    time_str = appointment_time_obj.strftime('%I:%M %p')
                except Exception:
                    time_str = appointment_time  # fallback to raw string if parsing fails
            elif hasattr(appointment_time, 'strftime'):
                time_str = appointment_time.strftime('%I:%M %p')
            else:
                time_str = str(appointment_time)

            time_label = UIHelpers.create_normal_label(
                apt_frame,
                time_str,
                text_color=UI_COLORS['primary']
            )

            time_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Patient info
            patient_label = UIHelpers.create_normal_label(
                apt_frame,
                f"{apt['patient_name']} ({apt['patient_id']})",
                text_color=UI_COLORS['text']
            )
            patient_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            # Status
            status_colors = {
                'Scheduled': UI_COLORS['primary'],
                'Completed': UI_COLORS['success'],
                'Cancelled': UI_COLORS['danger']
            }
            status_label = UIHelpers.create_normal_label(
                apt_frame,
                apt['status'],
                text_color=status_colors.get(apt['status'], UI_COLORS['text'])
            )
            status_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

            # Notes (if any)
            if apt.get('notes'):
                notes_label = UIHelpers.create_normal_label(
                    apt_frame,
                    f"Notes: {apt['notes'][:50]}...",
                    text_color=UI_COLORS['text_secondary']
                )
                notes_label.grid(row=1, column=1, columnspan=2, padx=10, pady=(0, 5), sticky="w")

            # Make clickable for editing
            for widget in [apt_frame, time_label, patient_label, status_label]:
                widget.bind("<Button-1>", lambda e, a=apt: self.select_appointment(a))
                widget.configure(cursor="hand2")

    def select_appointment(self, appointment):
        self.current_appointment = appointment
        self.populate_form(appointment)

    def populate_form(self, appointment):
        # Find patient in combo
        patient_text = f"{appointment['patient_id']} - {appointment['patient_name']}"
        try:
            self.patient_combo.set(patient_text)
        except:
            pass

        # Set date
        if isinstance(appointment['appointment_date'], str):
            apt_date = DateHelpers.string_to_date(appointment['appointment_date'])
        else:
            apt_date = appointment['appointment_date']
        self.date_entry.set_date(apt_date)

        # Set time safely
        apt_time = appointment['appointment_time']
        if isinstance(apt_time, str):
            time_str = apt_time
        elif isinstance(apt_time, datetime.timedelta):
            total_seconds = int(apt_time.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            time_str = f"{hours:02d}:{minutes:02d}"
        elif hasattr(apt_time, 'strftime'):
            time_str = apt_time.strftime('%H:%M')
        else:
            time_str = str(apt_time)
        self.time_combo.set(time_str)

        # Set status
        self.status_combo.set(appointment['status'])

        # Set notes (read-only)
        self.notes_textbox.delete("1.0", 'end')
        if appointment.get('notes'):
            self.notes_textbox.insert("1.0", appointment['notes'])

        # Disable all non-editable fields
        self.patient_combo.configure(state="disabled")
        self.date_entry.configure(state="disabled")
        self.time_combo.configure(state="disabled")
        self.notes_textbox.configure(state="disabled")

        # Enable only status
        self.status_combo.configure(state="normal")

        # Show update button, hide book button
        self.book_btn.grid_remove()
        self.update_btn.grid()

    def clear_form(self):
        self.current_appointment = None
        self.patient_combo.set("Select patient...")
        self.date_entry.set_date(date.today())

        self.status_combo.set("Scheduled")
        self.notes_textbox.delete("1.0", 'end')

        # Show book button, hide update button
        self.update_btn.grid_remove()
        self.book_btn.grid()
        self._on_date_change()

        # Re-enable fields for new booking
        self.patient_combo.configure(state="normal")
        self.date_entry.configure(state="normal")
        self.time_combo.configure(state="normal")
        self.notes_textbox.configure(state="normal")

    def book_appointment(self):
        # Validate form
        if not self.patient_combo.get():
            MessageHelpers.show_error("Validation Error", "Please select a patient",parent=self.window)
            return

        if not self.time_combo.get():
            MessageHelpers.show_error("Validation Error", "Please select appointment time",parent=self.window)
            return

        try:
            # Extract patient ID
            patient_id = self.patient_combo.get().split(' - ')[0]

            # Get form data
            apt_date = self.date_entry.get_date()
            apt_time = self.time_combo.get()
            notes = self.notes_textbox.get("1.0", 'end').strip()

            # Book appointment
            success, message = self.appointment_model.book_appointment(
                patient_id, apt_date, apt_time, notes
            )

            if success:
                MessageHelpers.show_success("Success", "Appointment booked successfully!",parent=self.window)
                self.clear_form()
                self.load_appointments()
            else:
                MessageHelpers.show_error("Error", message,parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to book appointment: {str(e)}",parent=self.window)

    def update_appointment(self):
        if not self.current_appointment:
            return

        try:
            # Update appointment status
            new_status = self.status_combo.get()
            success = self.appointment_model.update_appointment_status(
                self.current_appointment['id'], new_status
            )

            if success:
                MessageHelpers.show_success("Success", "Appointment updated successfully!",parent=self.window)
                self.load_appointments()
            else:
                MessageHelpers.show_error("Error", "Failed to update appointment",parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to update appointment: {str(e)}",parent=self.window)
