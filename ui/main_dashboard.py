import customtkinter as ctk
from database.models import PatientModel, AppointmentModel, MedicineModel, BillModel
from ui.patient_management import PatientManagementWindow
from ui.appointment_management import AppointmentManagementWindow
from ui.prescription_management import PrescriptionManagementWindow
from ui.medicine_management import MedicineManagementWindow
from ui.billing_management import BillingManagementWindow
from ui.reports_analytics import ReportsAnalyticsWindow
from utils.helpers import UIHelpers, MessageHelpers
from config import UI_COLORS
from datetime import date
import datetime


class MainDashboard:
    def __init__(self, doctor_info, on_logout_callback):
        self.doctor_info = doctor_info
        self.on_logout_callback = on_logout_callback

        # Initialize models
        self.patient_model = PatientModel()
        self.appointment_model = AppointmentModel()
        self.medicine_model = MedicineModel()
        self.bill_model = BillModel()

        # Create main window
        self.window = ctk.CTk()
        self.window.title(f"{doctor_info['clinic_name']} - Clinic Management System")
        # Get screen width and height
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Set the window size to cover the entire screen
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.minsize(1000, 600)

        # Configure grid
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.load_dashboard_data()
        self.window.mainloop()

    def setup_ui(self):
        # Sidebar
        self.setup_sidebar()

        # Main content area
        self.main_frame = UIHelpers.create_rounded_frame(
            self.window,
            fg_color=UI_COLORS['background'],
            corner_radius=0
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.setup_dashboard_content()

    def setup_sidebar(self):
        # Sidebar frame
        sidebar = UIHelpers.create_rounded_frame(
            self.window,
            fg_color=UI_COLORS['primary'],
            corner_radius=0,
            width=250
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        sidebar.grid_rowconfigure(8, weight=1)  # Push logout button to bottom
        sidebar.grid_propagate(False)

        # Clinic name and doctor info
        clinic_label = UIHelpers.create_subtitle_label(
            sidebar,
            self.doctor_info['clinic_name'],
            text_color="white"
        )
        clinic_label.grid(row=0, column=0, pady=(20, 5), padx=20, sticky="ew")

        doctor_label = UIHelpers.create_normal_label(
            sidebar,
            f"Dr. {self.doctor_info['doctor_name']}",
            text_color="white"
        )
        doctor_label.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="ew")

        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("👥 Patient Management", self.show_patient_management),
            ("📅 Appointments", self.show_appointment_management),
            ("💊 Medicine Management", self.show_medicine_management),
            ("📋 Prescriptions", self.show_prescription_management),
            ("💰 Billing", self.show_billing_management),
            ("📊 Reports & Analytics", self.show_reports_analytics)
        ]

        self.nav_buttons = {}
        for i, (text, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                fg_color="transparent",
                hover_color=UI_COLORS['hover'],
                anchor="w",
                height=40,
                font=('Arial', 12)
            )
            btn.grid(row=i + 2, column=0, pady=2, padx=10, sticky="ew")
            self.nav_buttons[text] = btn

        # Set dashboard as active initially
        self.set_active_nav("🏠 Dashboard")

        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            sidebar,
            text="🔓 Logout",
            command=self.logout,
            fg_color=UI_COLORS['danger'],
            hover_color="#C0392B",
            height=40
        )
        logout_btn.grid(row=9, column=0, pady=20, padx=10, sticky="ew")

    def setup_dashboard_content(self):
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)

        # Welcome message
        welcome_label = UIHelpers.create_title_label(
            header_frame,
            f"Welcome, Dr. {self.doctor_info['doctor_name']}",
            text_color=UI_COLORS['primary']
        )
        welcome_label.grid(row=0, column=0, sticky="w")

        # Date
        date_label = UIHelpers.create_normal_label(
            header_frame,
            f"Today: {date.today().strftime('%B %d, %Y')}",
            text_color=UI_COLORS['text_secondary']
        )
        date_label.grid(row=0, column=1, sticky="e")

        # Dashboard content
        self.dashboard_frame = UIHelpers.create_rounded_frame(
            self.main_frame,
            fg_color="transparent"
        )
        self.dashboard_frame.grid(row=1, column=0, sticky="nsew")
        self.dashboard_frame.grid_columnconfigure((0, 1), weight=1)
        self.dashboard_frame.grid_rowconfigure((0, 1), weight=1)

        # Quick stats cards
        self.setup_stats_cards()

        # Today's appointments
        self.setup_appointments_section()

        # Quick actions
        self.setup_quick_actions()

        # Alerts section
        self.setup_alerts_section()

    def setup_stats_cards(self):
        # Stats container
        stats_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Stats cards will be populated by load_dashboard_data
        self.stats_cards = {}

        # Total Patients
        self.stats_cards['patients'] = self.create_stat_card(stats_frame, "👥", "0", "Total Patients", 0)
        # Today's Appointments
        self.stats_cards['appointments'] = self.create_stat_card(stats_frame, "📅", "0", "Today's Appointments", 1)
        # Low Stock Medicines
        self.stats_cards['medicines'] = self.create_stat_card(stats_frame, "💊", "0", "Low Stock Items", 2)
        # Revenue This Month
        self.stats_cards['revenue'] = self.create_stat_card(stats_frame, "💰", "₹0", "This Month Revenue", 3)

    def create_stat_card(self, parent, icon, value, label, column):
        card = UIHelpers.create_rounded_frame(
            parent,
            fg_color=UI_COLORS['card'],
            corner_radius=15,
            height=120
        )
        card.grid(row=0, column=column, sticky="ew", padx=10)
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)
        card.grid_propagate(False)

        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=('Arial', 24)
        )
        icon_label.grid(row=0, column=0, pady=(15, 0))

        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=('Arial', 18, 'bold'),
            text_color=UI_COLORS['primary']
        )
        value_label.grid(row=1, column=0)

        # Label
        label_widget = ctk.CTkLabel(
            card,
            text=label,
            font=('Arial', 10),
            text_color=UI_COLORS['text_secondary']
        )
        label_widget.grid(row=2, column=0, pady=(0, 15))

        return {'card': card, 'value': value_label}

    def setup_appointments_section(self):
        # Appointments section
        appointments_frame = UIHelpers.create_rounded_frame(
            self.dashboard_frame,
            fg_color=UI_COLORS['card'],
            corner_radius=15
        )
        appointments_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        appointments_frame.grid_columnconfigure(0, weight=1)
        appointments_frame.grid_rowconfigure(1, weight=1)

        # Header
        apt_header = UIHelpers.create_subtitle_label(
            appointments_frame,
            "Today's Appointments",
            text_color=UI_COLORS['primary']
        )
        apt_header.grid(row=0, column=0, pady=15, sticky="w", padx=20)

        # Appointments list
        self.appointments_listbox = ctk.CTkScrollableFrame(
            appointments_frame,
            fg_color="transparent"
        )
        self.appointments_listbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

    def setup_quick_actions(self):
        # Quick actions section
        actions_frame = UIHelpers.create_rounded_frame(
            self.dashboard_frame,
            fg_color=UI_COLORS['card'],
            corner_radius=15
        )
        actions_frame.grid(row=1, column=1, sticky="nsew")
        actions_frame.grid_columnconfigure(0, weight=1)

        # Header
        actions_header = UIHelpers.create_subtitle_label(
            actions_frame,
            "Quick Actions",
            text_color=UI_COLORS['primary']
        )
        actions_header.grid(row=0, column=0, pady=15, sticky="w", padx=20)

        # Action buttons
        quick_actions = [
            ("Add New Patient", self.show_patient_management),
            ("Book Appointment", self.show_appointment_management),
            ("Create Prescription", self.show_prescription_management),
            ("Generate Bill", self.show_billing_management),
            ("View Reports", self.show_reports_analytics)
        ]

        for i, (text, command) in enumerate(quick_actions):
            btn = UIHelpers.create_styled_button(
                actions_frame,
                text,
                command,
                fg_color=UI_COLORS['secondary'],
                hover_color="#8B2E5B",
                width=200,
                height=35
            )
            btn.grid(row=i + 1, column=0, pady=5, padx=20)

    def setup_alerts_section(self):
        # This will show low stock medicines and other alerts
        # We'll populate this in load_dashboard_data
        pass

    def load_dashboard_data(self):
        try:
            # Load patient count
            patients = self.patient_model.get_all_patients()
            self.stats_cards['patients']['value'].configure(text=str(len(patients)))

            # Load today's appointments
            today_appointments = self.appointment_model.get_today_appointments()
            self.stats_cards['appointments']['value'].configure(text=str(len(today_appointments)))

            # Load and display today's appointments
            self.load_appointments_list(today_appointments)

            # Load low stock medicines
            low_stock = self.medicine_model.get_low_stock_medicines(10)
            self.stats_cards['medicines']['value'].configure(text=str(len(low_stock)))

            # ----- NEW REVENUE BLOCK -----
            # Calculate first and last day of the current month
            today = date.today()
            start_date = today.replace(day=1)
            end_date = today
            summary = self.bill_model.get_revenue_summary(start_date, end_date)
            if summary and summary.get("total_revenue") is not None:
                revenue = summary["total_revenue"]
            else:
                revenue = 0
            # Format as ₹ amount with two decimals.
            formatted_revenue = f"₹{revenue:,.2f}"
            self.stats_cards['revenue']['value'].configure(text=formatted_revenue)

            # ----- END BLOCK -----


        except Exception as e:
            print(f"Error loading dashboard data: {e}")

    def load_appointments_list(self, appointments):
        # Clear existing appointments
        for widget in self.appointments_listbox.winfo_children():
            widget.destroy()

        if not appointments:
            no_apt_label = UIHelpers.create_normal_label(
                self.appointments_listbox,
                "No appointments scheduled for today",
                text_color=UI_COLORS['text_secondary']
            )
            no_apt_label.pack(pady=20)
            return

        # Display appointments
        for apt in appointments:
            apt_frame = UIHelpers.create_rounded_frame(
                self.appointments_listbox,
                fg_color=UI_COLORS['background'],
                corner_radius=8,
                height=60
            )
            apt_frame.pack(fill="x", pady=2)
            apt_frame.grid_columnconfigure(1, weight=1)
            apt_frame.grid_propagate(False)

            appointment_time = apt['appointment_time']

            if isinstance(appointment_time, datetime.timedelta):
                # Manually format the timedelta as HH:MM
                total_seconds = int(appointment_time.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                time_str = f"{hours:02d}:{minutes:02d}"
            elif hasattr(appointment_time, "strftime"):
                # It's already datetime.time/datetime
                time_str = appointment_time.strftime('%I:%M %p')
            else:
                # Fallback if type is not as expected
                time_str = str(appointment_time)

            # Time
            time_label = UIHelpers.create_normal_label(
                apt_frame,
                time_str,
                text_color=UI_COLORS['primary']
            )
            time_label.grid(row=0, column=0, padx=10, pady=15, sticky="w")

            # Patient info
            patient_info = f"{apt['patient_name']} (ID: {apt['patient_id']})"
            patient_label = UIHelpers.create_normal_label(
                apt_frame,
                patient_info,
                text_color=UI_COLORS['text']
            )
            patient_label.grid(row=0, column=1, padx=10, pady=15, sticky="w")

            # Status
            status_color = {
                'Scheduled': UI_COLORS['primary'],
                'Completed': UI_COLORS['success'],
                'Cancelled': UI_COLORS['danger']
            }.get(apt['status'], UI_COLORS['text_secondary'])

            status_label = UIHelpers.create_normal_label(
                apt_frame,
                apt['status'],
                text_color=status_color
            )
            status_label.grid(row=0, column=2, padx=10, pady=15, sticky="e")

    def set_active_nav(self, active_text):
        # Reset all buttons
        for text, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent")

        # Set active button
        if active_text in self.nav_buttons:
            self.nav_buttons[active_text].configure(fg_color=UI_COLORS['hover'])

    def show_dashboard(self):
        self.set_active_nav("🏠 Dashboard")
        # Dashboard is already shown, just refresh data
        self.load_dashboard_data()

    def show_patient_management(self):
        self.set_active_nav("👥 Patient Management")
        try:
            patient_window = PatientManagementWindow(self.doctor_info)
            self.window.wait_window(patient_window.window)  # wait for patient window to close
            self.load_dashboard_data()
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to open Patient Management: {str(e)}", parent=self.window)

    def show_appointment_management(self):
        self.set_active_nav("📅 Appointments")
        try:
            appointment_window = AppointmentManagementWindow(self.doctor_info)
            self.window.wait_window(appointment_window.window)  # wait for appointment window to close
            self.load_dashboard_data()
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to open Appointment Management: {str(e)}", parent=self.window)

    def show_prescription_management(self):
        self.set_active_nav("📋 Prescriptions")
        try:
            prescription_window = PrescriptionManagementWindow(self.doctor_info)
            self.window.wait_window(prescription_window.window)  # wait for prescription window to close
            self.load_dashboard_data()

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to open Prescription Management: {str(e)}", parent=self.window)

    def show_medicine_management(self):
        self.set_active_nav("💊 Medicine Management")
        try:
            medicine_window = MedicineManagementWindow(self.doctor_info)
            self.window.wait_window(medicine_window.window)  # wait for medicine window to close
            self.load_dashboard_data()
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to open Medicine Management: {str(e)}", parent=self.window)

    def show_billing_management(self):
        self.set_active_nav("💰 Billing")
        try:
            billing_window = BillingManagementWindow(self.doctor_info)
            self.window.wait_window(billing_window.window)  # wait for billing window to close
            self.load_dashboard_data()
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to open Billing Management: {str(e)}", parent=self.window)

    def show_reports_analytics(self):
        self.set_active_nav("📊 Reports & Analytics")
        try:
            ReportsAnalyticsWindow(self.doctor_info)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to open Reports & Analytics: {str(e)}", parent=self.window)

    def logout(self):
        if MessageHelpers.ask_confirmation("Logout", "Are you sure you want to logout?", parent=self.window):
            self.window.destroy()
            if self.on_logout_callback:
                self.on_logout_callback()

    def destroy(self):
        self.window.destroy()
