import customtkinter as ctk
from database.models import PatientModel, AppointmentModel, MedicineModel, BillModel
from utils.helpers import UIHelpers, MessageHelpers
from utils.pdf_generator import PDFGenerator
from config import UI_COLORS
from tkcalendar import DateEntry
from datetime import date, timedelta
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ReportsAnalyticsWindow:
    def __init__(self, doctor_info):
        self.doctor_info = doctor_info
        self.patient_model = PatientModel()
        self.appointment_model = AppointmentModel()
        self.medicine_model = MedicineModel()
        self.bill_model = BillModel()

        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("Reports & Analytics")
        self.window.geometry("1050x600+10+10")
        self.window.transient()
        self.window.grab_set()

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Header
        header_label = UIHelpers.create_title_label(
            main_frame,
            "Reports & Analytics",
            text_color=UI_COLORS['primary']
        )
        header_label.grid(row=0, column=0, pady=(0, 20))

        # Content with tabs
        self.setup_tabs(main_frame)

    def setup_tabs(self, parent):
        # Create tabview
        tabview = ctk.CTkTabview(parent)
        tabview.grid(row=1, column=0, sticky="nsew")

        # Create tabs
        patient_tab = tabview.add("Patient Reports")
        appointment_tab = tabview.add("Appointments")
        medicine_tab = tabview.add("Medicine Reports")
        revenue_tab = tabview.add("Revenue Reports")

        # Setup each tab
        self.setup_patient_reports(patient_tab)
        self.setup_appointment_reports(appointment_tab)
        self.setup_medicine_reports(medicine_tab)
        self.setup_revenue_reports(revenue_tab)

    def setup_patient_reports(self, tab):
        # Configure tab grid for responsiveness
        tab.grid_rowconfigure(3, weight=1)  # Graph area grows vertically
        tab.grid_columnconfigure(0, weight=1)  # Whole content expands horizontally

        # === Quick Reports Toolbar ===
        quick_reports = UIHelpers.create_rounded_frame(tab, corner_radius=10, fg_color="#E0F7FA")  # Light cyan
        quick_reports.grid(row=0, column=0, sticky="ew", pady=10, padx=10)
        quick_reports.grid_columnconfigure(tuple(range(6)), weight=1)

        UIHelpers.create_section_label(
            quick_reports,
            "📊 Quick Reports",
            font=("Arial", 16, "bold"),
            text_color="#00796B",
            anchor="center"  # Center the text
        ).grid(row=0, column=0, columnspan=6, pady=(8, 12), sticky="nsew")

        # Predefined buttons
        button_bg = "#B2EBF2"  # Slightly darker cyan
        button_hover = "#4DD0E1"
        button_text = "#006064"

        periods = ["Today", "This Week", "This Month", "This Year"]
        for idx, period in enumerate(periods):
            UIHelpers.create_styled_button(
                quick_reports,
                period,
                fg_color=button_bg,
                hover_color=button_hover,
                text_color=button_text,
                command=lambda p=period.lower(): self.load_patient_report(p)
            ).grid(row=1, column=idx, padx=5, pady=5, sticky="ew")


        # PDF Quick Export buttons
        UIHelpers.create_styled_button(
            quick_reports,
            "📄 All Patients",
            fg_color="#C8E6C9",
            hover_color="#A5D6A7",
            text_color="#1B5E20",
            command=self.generate_all_patients_report
        ).grid(row=1, column=4, padx=5, pady=5, sticky="ew")

        UIHelpers.create_styled_button(
            quick_reports,
            "📄 Recent Patients (30 Days)",
            fg_color="#FFF9C4",
            hover_color="#FFF59D",
            text_color="#F57F17",
            command=self.generate_recent_patients_report
        ).grid(row=1, column=5, padx=5, pady=5, sticky="ew")

        # === Custom Range Reports ===
        custom_frame = UIHelpers.create_rounded_frame(tab, corner_radius=10, fg_color="#FCE4EC")  # Soft pink
        custom_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=10)
        for col in range(5):
            custom_frame.grid_columnconfigure(col, weight=1)

        UIHelpers.create_section_label(
            custom_frame,
            "📅 Custom Date Range",
            font=("Arial", 14, "bold"),
            text_color="#C2185B",
            anchor="center"
        ).grid(row=0, column=0, columnspan=5, pady=(6, 10), sticky="nsew")

        UIHelpers.create_normal_label(custom_frame, "From:", text_color="#880E4F") \
            .grid(row=1, column=0, padx=10, sticky="e")
        self.patient_start_date = DateEntry(
            custom_frame,
            width=12,
            background='#C2185B',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.patient_start_date.grid(row=1, column=1, padx=10, sticky="ew")
        self.patient_start_date.set_date(date.today() - timedelta(days=30))

        UIHelpers.create_normal_label(custom_frame, "To:", text_color="#880E4F") \
            .grid(row=1, column=2, padx=10, sticky="e")
        self.patient_end_date = DateEntry(
            custom_frame,
            width=12,
            background='#C2185B',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.patient_end_date.grid(row=1, column=3, padx=10, sticky="ew")
        self.patient_end_date.set_date(date.today())

        UIHelpers.create_styled_button(
            custom_frame,
            "🔍 Load",
            fg_color="#F48FB1",
            hover_color="#F06292",
            width=100,
            text_color="#880E4F",
            command=lambda: self.load_patient_report('custom')
        ).grid(row=1, column=4, padx=15, sticky="ew")

        # 📄 Download button
        UIHelpers.create_styled_button(
            custom_frame,
            "📄 Custom Download",
            fg_color="#D1C4E9",
            hover_color="#B39DDB",
            text_color="#4A148C",
            command=self.generate_custom_patients_report
        ).grid(row=1, column=5, padx=10, sticky="ew")

        # === Report Summary Area ===
        self.patient_report_summary = UIHelpers.create_rounded_frame(tab, corner_radius=10,
                                                                     fg_color="#FFF3E0")  # Pastel orange
        self.patient_report_summary.grid(row=2, column=0, sticky="ew", pady=10, padx=10)
        self.patient_report_summary.grid_columnconfigure(0, weight=1)

        UIHelpers.create_section_label(
            self.patient_report_summary,
            "📝 Report Summary",
            font=("Arial", 16, "bold"),
            text_color="#FB8C00",
            anchor="center"
        ).grid(row=0, column=0, sticky="nsew", pady=6, padx=10)

        self.report_summary_text = UIHelpers.create_normal_label(
            self.patient_report_summary,
            "Select a period or custom range to view summary...",
            text_color="#795548"
        )
        self.report_summary_text.grid(row=1, column=0, sticky="w", padx=15, pady=5)

        # === Graph Area ===
        self.patient_report_graph = UIHelpers.create_rounded_frame(tab, corner_radius=10,
                                                                   fg_color="#E8F5E9")  # Pastel green
        self.patient_report_graph.grid(row=3, column=0, sticky="nsew", pady=8, padx=10)
        self.patient_report_graph.grid_columnconfigure(0, weight=1)
        self.patient_report_graph.grid_rowconfigure(1, weight=1)

        UIHelpers.create_section_label(
            self.patient_report_graph,
            "📈 Report Visualization",
            font=("Arial", 16, "bold"),
            text_color="#388E3C",
            anchor="center"
        ).grid(row=0, column=0, sticky="nsew", pady=6, padx=10)

    def generate_custom_patients_report(self):
        try:
            start_date = self.patient_start_date.get_date()
            end_date = self.patient_end_date.get_date()

            if start_date > end_date:
                MessageHelpers.show_error("Error", "Invalid date range", parent=self.window)
                return

            patients = self.patient_model.get_all_patients()
            custom_patients = [
                p for p in patients if start_date <= p['created_at'].date() <= end_date
            ]

            if not custom_patients:
                MessageHelpers.show_success("No Data", "No patients found in this date range", parent=self.window)
                return

            headers = ['Patient ID', 'Name', 'Age', 'Gender', 'Phone', 'Registration Date']
            data = []
            for patient in custom_patients:
                reg_date = patient['created_at'].strftime('%d-%m-%Y')
                data.append([
                    patient['patient_id'],
                    patient['name'],
                    str(patient['age']),
                    patient['gender'],
                    patient['phone'] or 'N/A',
                    reg_date
                ])

            pdf_generator = PDFGenerator(
                self.doctor_info['clinic_name'],
                self.doctor_info['doctor_name']
            )

            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            filename = f"{downloads_dir}/custom_patients_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"

            success, message = pdf_generator.generate_report(
                f"Patients Report ({start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')})",
                data, headers, filename
            )

            if success:
                MessageHelpers.show_success("Success", f"Report generated successfully!\nSaved as: {filename}",
                                            parent=self.window)
            else:
                MessageHelpers.show_error("Error", message, parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate custom report: {str(e)}", parent=self.window)

    def load_patient_report(self, period):
        try:
            today = date.today()
            if period == 'today':
                start_date = end_date = today
            elif period == 'this week':
                start_date = today - timedelta(days=today.weekday())
                end_date = today
            elif period == 'this month':
                start_date = today.replace(day=1)
                end_date = today
            elif period == 'this year':
                start_date = today.replace(month=1, day=1)
                end_date = today
            elif period == 'custom':
                start_date = self.patient_start_date.get_date()
                end_date = self.patient_end_date.get_date()
                if start_date > end_date:
                    MessageHelpers.show_error("Error", "Invalid date range", parent=self.window)
                    return
            else:
                MessageHelpers.show_error("Error", "Invalid period", parent=self.window)
                return

            # Get patient stats from DB/model
            patients_per_day = self.patient_model.get_patient_counts_grouped_by_date(start_date, end_date)

            # --- Clear previous summary ---
            for widget in self.patient_report_summary.winfo_children():
                widget.destroy()

            total_patients = sum(patients_per_day.values()) if patients_per_day else 0

            # Create a card-style summary
            summary_frame = UIHelpers.create_rounded_frame(
                self.patient_report_summary,
                corner_radius=15,
                fg_color="#E0F7FA"  # light pastel cyan
            )
            summary_frame.pack(fill="x", padx=15, pady=10)

            UIHelpers.create_normal_label(
                summary_frame,
                f"Total Patients Registered: {total_patients}",

                text_color="#00796B"
            ).pack(padx=10, pady=10, anchor="center")

            # --- Clear previous graph ---
            for widget in self.patient_report_graph.winfo_children():
                widget.destroy()

            if patients_per_day:
                # Matplotlib Figure
                fig = Figure(figsize=(8, 3), dpi=100)
                ax = fig.add_subplot(111)
                fig.subplots_adjust(bottom=0.25)

                # Prepare data
                dates = sorted(patients_per_day.keys())
                counts = [patients_per_day[d] for d in dates]

                ax.bar([d.strftime("%d-%b") for d in dates], counts, color="#4DD0E1")  # soft cyan bars
                ax.set_title(f"Patient Registration Trend: {period.title()}", fontsize=14, color="#00796B")
                ax.set_xlabel("Date", fontsize=12, color="#004D40")
                ax.set_ylabel("Number of Patients", fontsize=12, color="#004D40")
                ax.tick_params(axis='x', rotation=45)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                canvas = FigureCanvasTkAgg(fig, master=self.patient_report_graph)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            else:
                # No data message in a card
                no_data_frame = UIHelpers.create_rounded_frame(
                    self.patient_report_graph,
                    corner_radius=15,
                    fg_color="#FFEBEE"  # soft red background
                )
                no_data_frame.pack(fill="both", expand=True, padx=20, pady=20)
                UIHelpers.create_normal_label(
                    no_data_frame,
                    "No patient data found for this period.",

                    text_color="#C62828"
                ).pack(expand=True, anchor="center", pady=20)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to load patient report: {str(e)}", parent=self.window)

    def setup_appointment_reports(self, tab):
        # Configure grid for responsiveness
        tab.grid_rowconfigure(3, weight=1)  # Graph area expands
        tab.grid_columnconfigure(0, weight=1)

        # === Title ===
        UIHelpers.create_section_label(
            tab,
            "📅 Appointment Reports",
            font=("Arial", 18, "bold"),
            text_color="#1565C0",  # Deep blue
            anchor="center"
        ).grid(row=0, column=0, pady=12, sticky="nsew")

        # === Date Range Selection ===
        date_frame = UIHelpers.create_rounded_frame(
            tab, fg_color="#E3F2FD", corner_radius=10  # Light blue background
        )
        date_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        for col in range(5):
            date_frame.grid_columnconfigure(col, weight=1)

        UIHelpers.create_normal_label(
            date_frame, "Select Date Range:", text_color="#0D47A1"
        ).grid(row=0, column=0, columnspan=5, pady=(8, 6))

        UIHelpers.create_normal_label(date_frame, "From:", text_color="#1565C0") \
            .grid(row=1, column=0, padx=10, sticky="e")
        self.apt_start_date = DateEntry(
            date_frame, width=12, background='#1565C0', foreground='white',
            borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.apt_start_date.grid(row=1, column=1, padx=5, sticky="ew")
        self.apt_start_date.set_date(date.today() - timedelta(days=30))

        UIHelpers.create_normal_label(date_frame, "To:", text_color="#1565C0") \
            .grid(row=1, column=2, padx=10, sticky="e")
        self.apt_end_date = DateEntry(
            date_frame, width=12, background='#1565C0', foreground='white',
            borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.apt_end_date.grid(row=1, column=3, padx=5, sticky="ew")
        self.apt_end_date.set_date(date.today())

        UIHelpers.create_styled_button(
            date_frame,
            "🔍 Generate Report",
            fg_color="#64B5F6",
            hover_color="#42A5F5",
            text_color="#0D47A1",
            command=self.generate_appointment_report
        ).grid(row=1, column=4, padx=15, sticky="ew")
        UIHelpers.create_styled_button(
            date_frame,
            "Download PDF",
            command=self.download_appointment_pdf,
            width=120
        ).grid(row=1, column=5, padx=10)

        # === Summary Section ===
        self.apt_summary_frame = UIHelpers.create_rounded_frame(
            tab, fg_color="#FFF3E0", corner_radius=10  # Soft orange
        )
        self.apt_summary_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.apt_summary_frame.grid_columnconfigure(0, weight=1)

        UIHelpers.create_section_label(
            self.apt_summary_frame,
            "📝 Appointment Summary",
            font=("Arial", 16, "bold"),
            text_color="#EF6C00",
            anchor="center"
        ).grid(row=0, column=0, pady=(8, 6))

        self.apt_summary_text = UIHelpers.create_normal_label(
            self.apt_summary_frame,
            "Select a range to view appointment summary...",
            text_color="#6D4C41"
        )
        self.apt_summary_text.grid(row=1, column=0, padx=15, pady=6, sticky="w")

        # === Graph Area ===
        self.apt_graph_frame = UIHelpers.create_rounded_frame(
            tab, fg_color="#E8F5E9", corner_radius=10  # Pastel green
        )
        self.apt_graph_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        self.apt_graph_frame.grid_columnconfigure(0, weight=1)
        self.apt_graph_frame.grid_rowconfigure(1, weight=1)

        UIHelpers.create_section_label(
            self.apt_graph_frame,
            "📊 Appointment Visualization",
            font=("Arial", 16, "bold"),
            text_color="#2E7D32",
            anchor="center"
        ).grid(row=0, column=0, pady=(8, 6), sticky="nsew")

        # Placeholder text until a graph is generated
        self.apt_graph_placeholder = UIHelpers.create_normal_label(
            self.apt_graph_frame,
            "Graphs will appear here after generating report...",
            text_color="#388E3C"
        )
        self.apt_graph_placeholder.grid(row=1, column=0, pady=20)

    def setup_medicine_reports(self, tab):
        # --- Title ---
        UIHelpers.create_subtitle_label(
            tab, "Medicine Reports", text_color=UI_COLORS['primary']
        ).grid(row=0, column=0, pady=10, sticky="w")

        # --- Medicine Stats ---
        med_frame = UIHelpers.create_rounded_frame(
            tab,
            fg_color=UI_COLORS['card'],
            corner_radius=10
        )
        med_frame.grid(row=1, column=0, sticky="ew", pady=10)
        med_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.medicine_stats = {}
        self.medicine_stats['total'] = self.create_stat_widget(med_frame, "Total Medicines", "0", 0)
        self.medicine_stats['low_stock'] = self.create_stat_widget(med_frame, "Low Stock", "0", 1)
        self.medicine_stats['expired'] = self.create_stat_widget(med_frame, "Near Expiry", "0", 2)

        # --- Graph Container ---
        graph_frame = UIHelpers.create_rounded_frame(
            tab,
            fg_color=UI_COLORS['card'],
            corner_radius=10
        )
        graph_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Placeholder data
        stats_values = [0, 0, 0]
        labels = ["Total", "Low Stock", "Near Expiry"]

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(labels, stats_values, color=["#4CAF50", "#F39C12", "#E74C3C"])
        ax.set_title("Medicine Stock Overview", fontsize=14)
        ax.set_ylabel("Count")
        ax.set_ylim(0, max(stats_values + [1]))

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.medicine_graph = {'fig': fig, 'ax': ax, 'canvas': canvas, 'bars': bars}

        # --- Generate Reports (Buttons Centered) ---
        report_frame = UIHelpers.create_rounded_frame(
            tab,
            fg_color=UI_COLORS['card'],
            corner_radius=10
        )
        report_frame.grid(row=3, column=0, pady=10, sticky="ew")
        report_frame.grid_columnconfigure(0, weight=1)

        button_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        button_frame.grid(row=0, column=0, pady=20)

        # Center buttons using grid with padding
        UIHelpers.create_styled_button(
            button_frame,
            "Stock Report",
            command=self.generate_stock_report,
            width=120
        ).grid(row=0, column=0, padx=10)

        UIHelpers.create_styled_button(
            button_frame,
            "Low Stock Alert",
            command=self.generate_low_stock_report,
            fg_color=UI_COLORS['danger'],
            hover_color="#C0392B",
            width=120
        ).grid(row=0, column=1, padx=10)

        UIHelpers.create_styled_button(
            button_frame,
            "Expiry Report",
            command=self.generate_expiry_report,
            fg_color=UI_COLORS['secondary'],
            hover_color="#8B2E5B",
            width=120
        ).grid(row=0, column=2, padx=10)

        # --- Load stats and update graph ---
        self.load_medicine_stats()
        self.update_medicine_graph()

    # --- Function to update the graph dynamically ---
    def update_medicine_graph(self):
        total = int(self.medicine_stats['total'].cget("text"))
        low = int(self.medicine_stats['low_stock'].cget("text"))
        expired = int(self.medicine_stats['expired'].cget("text"))

        values = [total, low, expired]

        for bar, val in zip(self.medicine_graph['bars'], values):
            bar.set_height(val)

        self.medicine_graph['ax'].set_ylim(0, max(values + [1]))
        self.medicine_graph['canvas'].draw()

    def setup_revenue_reports(self, tab):
        # --- Title ---
        UIHelpers.create_subtitle_label(
            tab, "Revenue Reports", text_color=UI_COLORS['primary']
        ).grid(row=0, column=0, pady=10, sticky="w")



        # --- Revenue Period Selection ---
        period_frame = UIHelpers.create_rounded_frame(
            tab,
            fg_color=UI_COLORS['card'],
            corner_radius=10
        )
        period_frame.grid(row=1, column=0, sticky="ew", pady=10)
        period_frame.grid_columnconfigure(0, weight=1)

        UIHelpers.create_normal_label(
            period_frame, "Select Period:", text_color=UI_COLORS['text']
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        period_buttons = ctk.CTkFrame(period_frame, fg_color="transparent")
        period_buttons.grid(row=1, column=0, pady=10)
        period_buttons.grid_columnconfigure(tuple(range(9)), weight=1)  # for 9 columns

        # --- Predefined period buttons ---
        self.revenue_period_buttons = {}

        self.revenue_period_buttons['today'] = UIHelpers.create_styled_button(
            period_buttons, "Today", command=lambda: self.on_revenue_period_select('today'), width=80
        )
        self.revenue_period_buttons['today'].grid(row=0, column=0, padx=5)

        self.revenue_period_buttons['week'] = UIHelpers.create_styled_button(
            period_buttons, "This Week", command=lambda: self.on_revenue_period_select('week'), width=80
        )
        self.revenue_period_buttons['week'].grid(row=0, column=1, padx=5)

        self.revenue_period_buttons['month'] = UIHelpers.create_styled_button(
            period_buttons, "This Month", command=lambda: self.on_revenue_period_select('month'), width=80
        )
        self.revenue_period_buttons['month'].grid(row=0, column=2, padx=5)

        self.revenue_period_buttons['year'] = UIHelpers.create_styled_button(
            period_buttons, "This Year", command=lambda: self.on_revenue_period_select('year'), width=80
        )
        self.revenue_period_buttons['year'].grid(row=0, column=3, padx=5)

        # --- Custom date range directly as DateEntry + Generate button ---
        UIHelpers.create_normal_label(period_buttons, "From:", text_color=UI_COLORS['text']).grid(row=0, column=4,
                                                                                                  padx=(10, 2))
        self.custom_start = DateEntry(period_buttons, width=12, background='darkblue', foreground='white',
                                      borderwidth=2, year=date.today().year)
        self.custom_start.grid(row=0, column=5, padx=2)

        UIHelpers.create_normal_label(period_buttons, "To:", text_color=UI_COLORS['text']).grid(row=0, column=6,
                                                                                                padx=(10, 2))
        self.custom_end = DateEntry(period_buttons, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    year=date.today().year)
        self.custom_end.grid(row=0, column=7, padx=2)

        UIHelpers.create_styled_button(
            period_buttons,
            "Generate",
            command=lambda: self.on_revenue_period_select('custom'),
            width=80
        ).grid(row=0, column=8, padx=10)

        # --- Data and Graph Frames (side by side) ---
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.grid(row=2, column=0, sticky="nsew", pady=10)
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure((0, 1), weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.revenue_data_frame = UIHelpers.create_rounded_frame(container, fg_color=UI_COLORS['background'],
                                                                 corner_radius=10)
        self.revenue_data_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.revenue_graph_frame = UIHelpers.create_rounded_frame(container, fg_color=UI_COLORS['background'],
                                                                  corner_radius=10)
        self.revenue_graph_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # --- Download PDF button ---
        self.download_pdf_btn = UIHelpers.create_styled_button(
            tab, "Download PDF", command=self.download_revenue_pdf, width=120
        )
        self.download_pdf_btn.grid(row=3, column=0, pady=10)

        # --- Placeholder Graph ---
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title("Revenue Overview", fontsize=14)
        ax.set_ylabel("Revenue")
        ax.set_xlabel("Period")
        canvas = FigureCanvasTkAgg(fig, master=self.revenue_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.revenue_graph = {'fig': fig, 'ax': ax, 'canvas': canvas}
        self.selected_revenue_period = None

    def create_stat_widget(self, parent, label, value, column):
        stat_frame = ctk.CTkFrame(parent, fg_color=UI_COLORS['background'], corner_radius=8)
        stat_frame.grid(row=0, column=column, padx=10, pady=10, sticky="ew")

        value_label = UIHelpers.create_subtitle_label(
            stat_frame, value, text_color=UI_COLORS['primary']
        )
        value_label.pack(pady=(10, 5))

        label_widget = UIHelpers.create_normal_label(
            stat_frame, label, text_color=UI_COLORS['text']
        )
        label_widget.pack(pady=(0, 10))

        return value_label



    def load_medicine_stats(self):
        try:
            medicines = self.medicine_model.get_all_medicines()
            total = len(medicines)

            low_stock = len(self.medicine_model.get_low_stock_medicines(10))

            # Count near expiry (within 30 days)
            near_expiry = 0
            cutoff_date = date.today() + timedelta(days=30)
            for med in medicines:
                if med['expiry_date'] and med['expiry_date'] <= cutoff_date:
                    near_expiry += 1

            self.medicine_stats['total'].configure(text=str(total))
            self.medicine_stats['low_stock'].configure(text=str(low_stock))
            self.medicine_stats['expired'].configure(text=str(near_expiry))

        except Exception as e:
            print(f"Error loading medicine stats: {e}")

    def download_appointment_pdf(self):
        try:
            start_date = self.apt_start_date.get_date()
            end_date = self.apt_end_date.get_date()

            if start_date > end_date:
                MessageHelpers.show_error("Error", "Invalid date range", parent=self.window)
                return

            # Fetch appointments in the range
            appointments = self.appointment_model.get_appointments_by_date_range(start_date, end_date)

            if not appointments:
                MessageHelpers.show_success("No Data", "No appointments found in this date range", parent=self.window)
                return

            headers = ['Appointment ID', 'Patient Name', 'Date', 'Time']
            data = []

            for apt in appointments:
                # --- Convert date ---
                apt_date = apt['appointment_date'].strftime('%d-%m-%Y') if apt['appointment_date'] else ''

                # --- Convert timedelta to HH:MM string ---
                if apt['appointment_time'] is not None:
                    total_seconds = apt['appointment_time'].total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    apt_time = f"{hours:02d}:{minutes:02d}"
                else:
                    apt_time = ''



                data.append([
                    apt['id'],
                    apt['patient_name'],

                    apt_date,
                    apt_time,

                ])

            pdf_gen = PDFGenerator(self.doctor_info['clinic_name'], self.doctor_info['doctor_name'])
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            filename = f"{downloads_dir}/appointments_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"

            success, message = pdf_gen.generate_report(
                f"Appointments Report ({start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')})",
                data, headers, filename
            )

            if success:
                MessageHelpers.show_success(
                    "Success",
                    f"Appointments report generated!\nSaved as: {filename}",
                    parent=self.window
                )
            else:
                MessageHelpers.show_error("Error", message, parent=self.window)

        except Exception as e:
            MessageHelpers.show_error(
                "Error",
                f"Failed to generate appointment report: {str(e)}",
                parent=self.window
            )

    def generate_all_patients_report(self):
        try:
            patients = self.patient_model.get_all_patients()

            if not patients:
                MessageHelpers.show_success("No Data", "No patients found to generate report", parent=self.window)
                return

            # Prepare data for PDF
            headers = ['Patient ID', 'Name', 'Age', 'Gender', 'Phone', 'Registration Date']
            data = []

            for patient in patients:
                # If created_at is datetime object, use .strftime directly, no slicing
                reg_date = patient['created_at'].strftime('%d-%m-%Y')

                data.append([
                    patient['patient_id'],
                    patient['name'],
                    str(patient['age']),
                    patient['gender'],
                    patient['phone'] or 'N/A',
                    reg_date
                ])

            # Generate PDF
            pdf_generator = PDFGenerator(
                self.doctor_info['clinic_name'],
                self.doctor_info['doctor_name']
            )

            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            filename = f"{downloads_dir}/all_patients_report_{date.today().strftime('%Y%m%d')}.pdf"

            success, message = pdf_generator.generate_report(
                "All Patients Report", data, headers, filename
            )

            if success:
                MessageHelpers.show_success("Success", f"Report generated successfully!\nSaved as: {filename}",
                                            parent=self.window)
            else:
                MessageHelpers.show_error("Error", message, parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate report: {str(e)}", parent=self.window)

    def generate_recent_patients_report(self):
        # Generate report for patients registered in last 30 days
        try:
            patients = self.patient_model.get_all_patients()
            cutoff_date = date.today() - timedelta(days=30)

            recent_patients = [p for p in patients if p['created_at'].date() >= cutoff_date]

            if not recent_patients:
                MessageHelpers.show_success("No Data", "No recent patients found (last 30 days)", parent=self.window)
                return

            # Same logic as all patients but with filtered data
            headers = ['Patient ID', 'Name', 'Age', 'Gender', 'Phone', 'Registration Date']
            data = []

            for patient in recent_patients:
                # If created_at is datetime object, use .strftime directly, no slicing
                reg_date = patient['created_at'].strftime('%d-%m-%Y')

                data.append([
                    patient['patient_id'],
                    patient['name'],
                    str(patient['age']),
                    patient['gender'],
                    patient['phone'] or 'N/A',
                    reg_date
                ])

            # Generate PDF
            pdf_generator = PDFGenerator(
                self.doctor_info['clinic_name'],
                self.doctor_info['doctor_name']
            )

            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            filename = f"{downloads_dir}/recent_patients_report_{date.today().strftime('%Y%m%d')}.pdf"

            success, message = pdf_generator.generate_report(
                "Recent Patients Report (Last 30 Days)", data, headers, filename
            )

            if success:
                MessageHelpers.show_success("Success", f"Report generated successfully!\nSaved as: {filename}",
                                            parent=self.window)
            else:
                MessageHelpers.show_error("Error", message, parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate report: {str(e)}", parent=self.window)

    def generate_appointment_report(self):
        try:
            start_date = self.apt_start_date.get_date()
            end_date = self.apt_end_date.get_date()

            if start_date > end_date:
                MessageHelpers.show_error("Error", "Invalid date range", parent=self.window)
                return

            # Fetch appointment stats from DB/model
            appointments_per_day, _ = self.appointment_model.get_appointment_stats(start_date, end_date)

            # Clear old summary + graphs
            for widget in self.apt_summary_frame.winfo_children():
                widget.destroy()
            for widget in self.apt_graph_frame.winfo_children():
                widget.destroy()

            # === Summary ===
            total_apts = sum(appointments_per_day.values()) if appointments_per_day else 0

            UIHelpers.create_section_label(
                self.apt_summary_frame,
                "📝 Appointment Summary",
                font=("Arial", 16, "bold"),
                text_color="#EF6C00"
            ).pack(pady=(8, 6))

            UIHelpers.create_normal_label(
                self.apt_summary_frame,
                f"Total Appointments: {total_apts}",
                text_color="#4E342E"
            ).pack(pady=8, padx=10, anchor="w")

            # === Graphs Container ===
            graphs_container = ctk.CTkFrame(self.apt_graph_frame, fg_color="transparent")
            graphs_container.pack(fill="both", expand=True)

            # --- Graph: Line chart (Appointments per day) ---
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            fig.subplots_adjust(bottom=0.25)

            if appointments_per_day:
                dates = sorted(appointments_per_day.keys())

                counts = [appointments_per_day[d] for d in dates]
                ax.plot([d.strftime("%d-%b") for d in dates], counts,
                        marker="o", color="#1565C0", linewidth=2)
                ax.set_title("Appointments per Day", fontsize=12, color="#0D47A1")
                ax.set_xlabel("Date")
                ax.set_ylabel("Appointments")
                ax.tick_params(axis="x", rotation=45)
            else:
                ax.text(0.5, 0.5, "No data found", ha="center", va="center")

            canvas = FigureCanvasTkAgg(fig, master=graphs_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to load appointment report: {str(e)}", parent=self.window)

    def generate_stock_report(self):
        try:
            medicines = self.medicine_model.get_all_medicines()
            if not medicines:
                MessageHelpers.show_success("No Data", "No medicines found to generate stock report",
                                            parent=self.window)
                return

            headers = ['Medicine ID', 'Name', 'Category', 'Manufacturer', 'Batch No', 'Expiry Date', 'Stock Quantity',
                       'Price']
            data = []
            for med in medicines:
                expiry = med['expiry_date'].strftime('%d-%m-%Y') if med.get('expiry_date') else 'N/A'
                data.append([
                    med['medicine_id'],
                    med['name'],
                    med['category'],
                    med['manufacturer'],
                    med['batch_no'],
                    expiry,
                    str(med['stock_quantity']),
                    f"{med['price']:.2f}"
                ])

            pdf_gen = PDFGenerator(self.doctor_info['clinic_name'], self.doctor_info['doctor_name'])
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            filename = f"{downloads_dir}/stock_report_{date.today().strftime('%Y%m%d')}.pdf"

            success, message = pdf_gen.generate_report("Stock Report", data, headers, filename)
            if success:
                MessageHelpers.show_success("Success", f"Stock report generated!\nSaved to: {filename}",
                                            parent=self.window)
            else:
                MessageHelpers.show_error("Error", message, parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate stock report: {str(e)}", parent=self.window)

    def generate_low_stock_report(self):
        try:
            threshold = 10  # Define low stock threshold
            medicines = self.medicine_model.get_low_stock_medicines(threshold)
            if not medicines:
                MessageHelpers.show_success("No Data", f"No medicines with stock lower than {threshold}",
                                            parent=self.window)
                return

            headers = ['Medicine ID', 'Name', 'Category', 'Manufacturer', 'Batch No', 'Expiry Date', 'Stock Quantity']
            data = []
            for med in medicines:
                expiry = med['expiry_date'].strftime('%d-%m-%Y') if med.get('expiry_date') else 'N/A'
                data.append([
                    med['medicine_id'],
                    med['name'],
                    med['category'],
                    med['manufacturer'],
                    med['batch_no'],
                    expiry,
                    str(med['stock_quantity'])
                ])

            pdf_gen = PDFGenerator(self.doctor_info['clinic_name'], self.doctor_info['doctor_name'])
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            filename = f"{downloads_dir}/low_stock_report_{date.today().strftime('%Y%m%d')}.pdf"

            success, message = pdf_gen.generate_report("Low Stock Report", data, headers, filename)
            if success:
                MessageHelpers.show_success("Success", f"Low stock report generated!\nSaved to: {filename}",
                                            parent=self.window)
            else:
                MessageHelpers.show_error("Error", message, parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate low stock report: {str(e)}", parent=self.window)

    def generate_expiry_report(self):
        try:
            medicines = self.medicine_model.get_all_medicines()
            if not medicines:
                MessageHelpers.show_success("No Data", "No medicines found to generate expiry report",
                                            parent=self.window)
                return

            cutoff_date = date.today() + timedelta(days=30)  # Define near expiry threshold
            near_expiry_meds = [med for med in medicines if
                                med.get('expiry_date') and med['expiry_date'] <= cutoff_date]

            if not near_expiry_meds:
                MessageHelpers.show_success("No Data", "No medicines near expiry within 30 days", parent=self.window)
                return

            headers = ['Medicine ID', 'Name', 'Category', 'Manufacturer', 'Batch No', 'Expiry Date', 'Stock Quantity']
            data = []
            for med in near_expiry_meds:
                expiry = med['expiry_date'].strftime('%d-%m-%Y') if med.get('expiry_date') else 'N/A'
                data.append([
                    med['medicine_id'],
                    med['name'],
                    med['category'],
                    med['manufacturer'],
                    med['batch_no'],
                    expiry,
                    str(med['stock_quantity'])
                ])

            pdf_gen = PDFGenerator(self.doctor_info['clinic_name'], self.doctor_info['doctor_name'])
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            filename = f"{downloads_dir}/expiry_report_{date.today().strftime('%Y%m%d')}.pdf"

            success, message = pdf_gen.generate_report("Expiry Report", data, headers, filename)
            if success:
                MessageHelpers.show_success("Success", f"Expiry report generated!\nSaved to: {filename}",
                                            parent=self.window)
            else:
                MessageHelpers.show_error("Error", message, parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate expiry report: {str(e)}", parent=self.window)

    def on_revenue_period_select(self, period):
        # --- Highlight selected button ---
        for key, btn in self.revenue_period_buttons.items():
            if key == period:
                btn.configure(fg_color=UI_COLORS['primary'], text_color="white")
            else:
                btn.configure(fg_color="#E0E0E0", text_color="#000")

        self.selected_revenue_period = period

        # Generate report
        self.generate_revenue_report(period)

    def generate_revenue_report(self, period):
        try:
            today = date.today()

            # Determine start and end dates
            if period == 'today':
                start_date = end_date = today
            elif period == 'week':
                start_date = today - timedelta(days=today.weekday())
                end_date = today
            elif period == 'month':
                start_date = today.replace(day=1)
                end_date = today
            elif period == 'year':
                start_date = today.replace(month=1, day=1)
                end_date = today
            elif period == 'custom':
                start_date = self.custom_start.get_date()  # returns datetime.date
                end_date = self.custom_end.get_date()
                if start_date > end_date:
                    MessageHelpers.show_error("Error", "Start date cannot be after end date", parent=self.window)
                    return
            else:
                MessageHelpers.show_error("Error", "Invalid period", parent=self.window)
                return

            # ✅ Store active dates for PDF download
            self.active_revenue_start_date = start_date
            self.active_revenue_end_date = end_date

            # --- Fetch data from model ---
            summary = self.bill_model.get_revenue_summary(start_date, end_date)
            revenue_over_time = self.bill_model.get_revenue_over_time(start_date,
                                                                      end_date)  # list of tuples (label, amount)

            # --- Clear previous data and graph ---
            for widget in self.revenue_data_frame.winfo_children():
                widget.destroy()
            self.revenue_graph['ax'].clear()

            if not summary:
                UIHelpers.create_normal_label(
                    self.revenue_data_frame,
                    "No revenue records found for selected period.",
                    text_color="#aa3333"
                ).pack(anchor="w", padx=20, pady=10)
                return

            # --- Display summary ---
            UIHelpers.create_subtitle_label(
                self.revenue_data_frame,
                f"Revenue Summary ({period.title()})",
                text_color="#222"
            ).pack(anchor="w", padx=20, pady=(10, 2))
            UIHelpers.create_normal_label(
                self.revenue_data_frame,
                f"Total Bills: {summary['total_bills'] or 0}",
                text_color="#333"
            ).pack(anchor="w", padx=40, pady=4)
            UIHelpers.create_normal_label(
                self.revenue_data_frame,
                f"Total Revenue: Rs. {summary['total_revenue'] or 0:.2f}",
                text_color="#0b6623"
            ).pack(anchor="w", padx=40, pady=4)
            UIHelpers.create_normal_label(
                self.revenue_data_frame,
                f"Consultation Revenue: Rs. {summary['consultation_revenue'] or 0:.2f}",
                text_color="#0b6623"
            ).pack(anchor="w", padx=40, pady=4)
            UIHelpers.create_normal_label(
                self.revenue_data_frame,
                f"Medicine Revenue: Rs. {summary['medicine_revenue'] or 0:.2f}",
                text_color="#0b6623"
            ).pack(anchor="w", padx=40, pady=4)

            # --- Plot graph ---

            if revenue_over_time:
                labels = [row['bill_date'].strftime("%d-%b") for row in revenue_over_time]
                amounts = [row['total_revenue'] for row in revenue_over_time]
                self.revenue_graph['ax'].bar(labels, amounts, color="#4CAF50")
                self.revenue_graph['ax'].set_title("Revenue Over Time")
                self.revenue_graph['ax'].set_ylabel("Revenue (Rs. )")
                self.revenue_graph['ax'].set_xlabel("Date")
            else:
                self.revenue_graph['ax'].text(0.5, 0.5, "No Data Found", ha="center", va="center")

            self.revenue_graph['canvas'].draw()

        except Exception as e:
            for widget in self.revenue_data_frame.winfo_children():
                widget.destroy()
            UIHelpers.create_normal_label(
                self.revenue_data_frame,
                f"Failed to generate revenue report: {str(e)}",
                text_color="#aa3333"
            ).pack(anchor="w", padx=40, pady=10)

    def download_revenue_pdf(self):
        try:
            # --- Use stored active dates ---
            start_date = getattr(self, 'active_revenue_start_date', None)
            end_date = getattr(self, 'active_revenue_end_date', None)
            if not start_date or not end_date:
                MessageHelpers.show_error("Error", "Please generate a report first", parent=self.window)
                return

            # Fetch revenue data
            revenue_over_time = self.bill_model.get_revenue_over_time(start_date, end_date)

            headers = ["Date", "Revenue (Rs.)"]
            data = [(row['bill_date'].strftime("%d-%b-%Y"), row['total_revenue']) for row in revenue_over_time]

            filename = f"downloads/revenue_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
            os.makedirs("downloads", exist_ok=True)
            pdf_gen = PDFGenerator(self.doctor_info['clinic_name'], self.doctor_info['doctor_name'])
            success, message = pdf_gen.generate_report(
                f"Revenue Report ({start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')})",
                data, headers, filename
            )

            if success:
                MessageHelpers.show_success("Success", f"Revenue report saved as {filename}", parent=self.window)
            else:
                MessageHelpers.show_error("Error", message, parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to download PDF: {str(e)}", parent=self.window)



