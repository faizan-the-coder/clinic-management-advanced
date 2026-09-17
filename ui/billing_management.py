import customtkinter as ctk
from database.models import BillModel, PatientModel
from utils.helpers import UIHelpers, MessageHelpers
from utils.pdf_generator import PDFGenerator
from config import UI_COLORS
from datetime import date
import os
import qrcode
import tkinter.ttk as ttk
from tkcalendar import DateEntry
from customtkinter import CTkImage

class BillingManagementWindow:
    def __init__(self, doctor_info):
        self.doctor_info = doctor_info
        self.bill_model = BillModel()
        self.patient_model = PatientModel()

        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("Billing Management")
        self.window.geometry("1000x690+10+0")
        self.window.transient()
        self.window.grab_set()

        self.setup_ui()
        self.setup_bills_tab()
        self.load_patients()

    def setup_ui(self):
        # Main container
        main_frame = UIHelpers.create_rounded_frame(
            self.window,
            fg_color=UI_COLORS['card'],
            corner_radius=15
        )
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Divide into left and right panels
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

        left_frame.grid(row=0, column=0, sticky="nsew", padx=(15, 10), pady=15)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 15), pady=15)

        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=1)

        # ---------------- LEFT SIDE (Form) ---------------- #
        header_label = UIHelpers.create_title_label(
            left_frame,
            "Generate Bill",
            text_color=UI_COLORS['primary']
        )
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        fields = [
            ("Patient*:", None, "patient_combo", "combo", ["Select patient"]),
            ("Consultation Fee (₹):", "500.00", "consultation_entry", "entry"),
            ("Medicine Charges (₹):", "0.00", "medicine_entry", "entry"),
            ("Lab Charges (₹):", "0.00", "lab_entry", "entry"),
            ("Other Charges (₹):", "0.00", "other_entry", "entry"),
            ("Discount (₹):", "0.00", "discount_entry", "entry"),
            ("Tax Rate (%):", "18.00", "tax_entry", "entry"),
        ]

        for i, (label, default, attr, ftype, *extra) in enumerate(fields, start=1):
            UIHelpers.create_normal_label(left_frame, label, text_color=UI_COLORS['text']).grid(
                row=i, column=0, sticky="w", padx=10, pady=6
            )
            if ftype == "entry":
                entry = UIHelpers.create_styled_entry(left_frame, placeholder_text=default, width=200)
                entry.insert(0, default)
                entry.grid(row=i, column=1, sticky="ew", padx=10, pady=6)
                setattr(self, attr, entry)
            elif ftype == "combo":
                combo = UIHelpers.create_styled_combobox(left_frame, values=[], width=220)
                combo.set(extra[0][0])
                combo.grid(row=i, column=1, sticky="ew", padx=10, pady=6)
                setattr(self, attr, combo)

        left_frame.grid_columnconfigure(1, weight=1)

        # Bind calculation
        for entry in [self.consultation_entry, self.medicine_entry,
                      self.lab_entry, self.other_entry,
                      self.discount_entry, self.tax_entry]:
            entry.bind('<KeyRelease>', self.calculate_total)

        # ---------------- RIGHT SIDE ---------------- #
        # Summary Frame
        summary_card = UIHelpers.create_rounded_frame(
            right_frame, fg_color=UI_COLORS['background'], corner_radius=12
        )
        summary_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 10))
        right_frame.grid_rowconfigure(0, weight=0)  # summary doesn't expand
        right_frame.grid_rowconfigure(1, weight=0)  # qr doesn't expand
        right_frame.grid_rowconfigure(2, weight=0)  # buttons fixed
        right_frame.grid_columnconfigure(0, weight=1)

        # Section heading
        UIHelpers.create_title_label(summary_card, "Summary", text_color=UI_COLORS['primary']).grid(
            row=0, column=0, columnspan=2, pady=(15, 10)
        )

        # Total
        UIHelpers.create_subtitle_label(summary_card, "Total Amount:", text_color=UI_COLORS['text']).grid(
            row=1, column=0, sticky="w", padx=15, pady=(10, 5)
        )
        self.total_label = UIHelpers.create_subtitle_label(
            summary_card, "₹0.00", text_color=UI_COLORS['success']
        )
        self.total_label.grid(row=1, column=1, sticky="e", padx=15, pady=(10, 5))

        # Payment Method
        UIHelpers.create_normal_label(summary_card, "Payment Method:", text_color=UI_COLORS['text']).grid(
            row=2, column=0, sticky="w", padx=15, pady=8
        )
        payment_methods = ["Cash", "UPI"]
        self.payment_combo = UIHelpers.create_styled_combobox(summary_card, values=payment_methods, width=150)
        self.payment_combo.set("Cash")
        self.payment_combo.grid(row=2, column=1, sticky="e", padx=15, pady=8)
        self.payment_combo.configure(command=self.on_payment_method_changed)

        # QR Frame (hidden initially, shown only on UPI)
        self.upi_qr_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.upi_qr_frame.grid(row=1, column=0, pady=(0, 15), sticky="nsew")
        self.upi_qr_frame.grid_columnconfigure(0, weight=1)
        self.upi_qr_label = ctk.CTkLabel(self.upi_qr_frame, text='')
        self.upi_qr_label.grid(row=0, column=0, padx=10, pady=10)
        self.upi_qr_frame.grid_remove()

        # Buttons Frame (always visible, outside summary)
        button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(10, 5))

        self.save_btn = UIHelpers.create_styled_button(
            button_frame, "Generate Bill",
            command=self.generate_bill,
            fg_color=UI_COLORS['primary'],
            hover_color=UI_COLORS['hover'],
            width=130
        )
        self.save_btn.grid(row=0, column=0, padx=8)

        pdf_btn = UIHelpers.create_styled_button(
            button_frame, "Generate PDF",
            command=self.generate_pdf,
            fg_color=UI_COLORS['success'],
            hover_color="#D68910",
            width=130
        )
        pdf_btn.grid(row=0, column=1, padx=8)

        clear_btn = UIHelpers.create_styled_button(
            button_frame, "Clear",
            command=self.clear_form,
            fg_color=UI_COLORS['text_secondary'],
            hover_color="#555555",
            width=90
        )
        clear_btn.grid(row=0, column=2, padx=8)

        # Initial total
        self.calculate_total()

    def setup_bills_tab(self):
        # ---------------- Main Frame ---------------- #
        bills_frame = ctk.CTkFrame(self.window, fg_color=UI_COLORS['card'], corner_radius=12)
        bills_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # ---------------- Filters Frame ---------------- #
        filter_frame = ctk.CTkFrame(bills_frame, fg_color=UI_COLORS['background'], corner_radius=10)
        filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        bills_frame.grid_columnconfigure(0, weight=1)

        # Search label + entry
        ctk.CTkLabel(filter_frame, text="Search:", text_color=UI_COLORS['text']).grid(row=0, column=0, padx=(10, 5),
                                                                                      pady=10)
        self.search_entry = ctk.CTkEntry(filter_frame, width=250, placeholder_text="Search by patient, bill ID...")
        self.search_entry.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_bills())

        # Date filters
        ctk.CTkLabel(filter_frame, text="From:", text_color=UI_COLORS['text']).grid(row=0, column=2, padx=(5, 5))
        self.search_start_date = DateEntry(filter_frame, width=12)
        self.search_start_date.grid(row=0, column=3, padx=(0, 15))

        ctk.CTkLabel(filter_frame, text="To:", text_color=UI_COLORS['text']).grid(row=0, column=4, padx=(5, 5))
        self.search_end_date = DateEntry(filter_frame, width=12)
        self.search_end_date.grid(row=0, column=5, padx=(0, 15))

        # Search button
        self.search_button = UIHelpers.create_styled_button(
            filter_frame, "Search", command=self.load_bills,
            fg_color=UI_COLORS['primary'], hover_color=UI_COLORS['hover'], width=100
        )
        self.search_button.grid(row=0, column=6, padx=10)

        # Allow filter_frame to expand properly
        filter_frame.grid_columnconfigure(1, weight=1)  # search entry expands
        for i in [0, 2, 3, 4, 5, 6]:
            filter_frame.grid_columnconfigure(i, weight=0)

        # ---------------- Table Frame ---------------- #
        table_frame = ctk.CTkFrame(bills_frame, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        bills_frame.grid_rowconfigure(1, weight=1)

        # Scrollbar + Treeview
        columns = ("bill_id", "patient_name", "bill_date", "total_amount", "payment_method")
        self.bills_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.bills_tree.yview)
        self.bills_tree.configure(yscrollcommand=vsb.set)

        # Layout with grid
        self.bills_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Column setup
        for col in columns:
            self.bills_tree.heading(col, text=col.replace("_", " ").title())
            if col == "patient_name":
                self.bills_tree.column(col, anchor="w", width=180)
            elif col == "bill_date":
                self.bills_tree.column(col, anchor="center", width=120)
            elif col == "total_amount":
                self.bills_tree.column(col, anchor="e", width=120)
            else:
                self.bills_tree.column(col, anchor="center", width=100)

        # Row double click action
        self.bills_tree.bind("<Double-1>", self.on_bill_row_double_click)

        # ---------------- Load Data ---------------- #
        self.load_bills()

    def on_bill_row_double_click(self, event):
        selected_item = self.bills_tree.focus()
        if not selected_item:
            return

        bill_values = self.bills_tree.item(selected_item, "values")
        # Assuming: bill_id, patient_name, bill_date, total_amount, payment_method
        bill_id = bill_values[0]

        # Fetch full bill from model by bill_id (should return all bill fields)
        bill = self.bill_model.get_bill_by_id(bill_id)
        if not bill:
            MessageHelpers.show_error("Error", "Bill not found.",parent=self.window)
            return

        # Fill form fields
        self.current_bill_id = bill["bill_id"]
        self.patient_combo.set(f"{bill['patient_id']} - {bill['patient_name']}")  # adjust if value differs
        self.consultation_entry.delete(0, "end")
        self.consultation_entry.insert(0, str(bill["consultation_fee"]))
        self.medicine_entry.delete(0, "end")
        self.medicine_entry.insert(0, str(bill["medicine_charges"]))
        self.lab_entry.delete(0, "end")
        self.lab_entry.insert(0, str(bill["lab_charges"]))
        self.other_entry.delete(0, "end")
        self.other_entry.insert(0, str(bill["other_charges"]))
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, str(bill["discount"]))
        self.tax_entry.delete(0, "end")
        self.tax_entry.insert(0, str(bill["tax_rate"]))
        self.payment_combo.set(bill["payment_method"])
        self.calculate_total()
        self.on_payment_method_changed(None)

        # Change button text for update
        self.save_btn.configure(text="Update Bill", command=self.update_bill)

    def update_bill(self):
        if not hasattr(self, "current_bill_id"):
            MessageHelpers.show_error("Error", "No bill selected for update.",parent=self.window)
            return
        try:
            patient_id = self.patient_combo.get().split(" - ")[0]
            consultation_fee = float(self.consultation_entry.get() or "0")
            medicine_charges = float(self.medicine_entry.get() or "0")
            lab_charges = float(self.lab_entry.get() or "0")
            other_charges = float(self.other_entry.get() or "0")
            discount = float(self.discount_entry.get() or "0")
            tax_rate = float(self.tax_entry.get() or "0")
            payment_method = self.payment_combo.get()
            bill_id = self.current_bill_id

            # Update in the model
            success, msg = self.bill_model.update_bill(
                bill_id, patient_id, consultation_fee, medicine_charges, lab_charges,
                other_charges, discount, tax_rate, payment_method
            )
            if success:
                MessageHelpers.show_success("Success", "Bill updated successfully!",parent=self.window)
                self.load_bills()
                self.save_btn.configure(text="Generate Bill", command=self.generate_bill)
                del self.current_bill_id
            else:
                MessageHelpers.show_error("Error", f"Failed to update bill: {msg}",parent=self.window)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Exception: {str(e)}",parent=self.window)

    def load_bills(self):
        search_term = self.search_entry.get().strip() or None
        start_date = self.search_start_date.get_date()
        end_date = self.search_end_date.get_date()
        bills = self.bill_model.get_bills(search=search_term, start_date=start_date, end_date=end_date)

        # Clear existing rows
        for item in self.bills_tree.get_children():
            self.bills_tree.delete(item)

        # Insert rows into tree
        for bill in bills:
            self.bills_tree.insert("", "end", values=(
                bill["bill_id"],
                bill["patient_name"],
                bill["bill_date"].strftime("%Y-%m-%d"),
                f"₹{bill['total_amount']:.2f}",
                bill["payment_method"]
            ))



    def on_payment_method_changed(self, event):
        selected = self.payment_combo.get()
        if selected == "UPI":
            upi_id = "kfaizan684.fk@okhdfcbank"  # Your clinic UPI ID

            # Get amount from total label
            amount_str = self.total_label.cget("text").replace("₹", "").strip()
            try:
                amount = float(amount_str)
            except ValueError:
                amount = None

            # Generate QR code (PIL Image)
            qr_img = self.generate_upi_qr_code(upi_id, name="Clinic Name", amount=amount)

            # Convert to CTkImage with fixed size (crisp scaling)
            qr_photo = CTkImage(light_image=qr_img, dark_image=qr_img, size=(150, 150))

            # Update the QR label
            self.upi_qr_label.configure(image=qr_photo, text="")
            self.upi_qr_label.image = qr_photo  # Prevent garbage collection

            # Show the frame centered
            self.upi_qr_frame.grid(row=10, column=0, columnspan=2, pady=15, sticky="nsew")
            self.upi_qr_frame.grid_columnconfigure(0, weight=1)  # Center align
        else:
            self.upi_qr_frame.grid_remove()  # Hide QR frame if not UPI

    def generate_upi_qr_code(self, upi_id, name=None, transaction_note=None, amount=None, currency="INR"):
        """
        Generate a UPI payment QR code image (PIL).
        :param upi_id: str - UPI ID (e.g. "shop@bank")
        :param name: str - Receiver's name (optional)
        :param transaction_note: str - Note for transaction (optional)
        :param amount: str or float - Amount to pay (optional)
        :param currency: str - Currency code, default INR
        :return: PIL Image object
        """
        # Construct UPI URI
        upi_uri = f"upi://pay?pa={upi_id}"
        if name:
            upi_uri += f"&pn={name}"
        if transaction_note:
            upi_uri += f"&tn={transaction_note}"
        if amount is not None:
            upi_uri += f"&am={amount}&cu={currency}"

        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(upi_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to RGB PIL image (important for CTkImage)
        return img.convert("RGB")

    def load_patients(self):
        try:
            patients = self.patient_model.get_all_patients()
            patient_options = [f"{p['patient_id']} - {p['name']}" for p in patients]
            self.patient_combo.configure(values=patient_options)
        except Exception as e:
            print(f"Error loading patients: {e}")

    def calculate_total(self, event=None):
        try:
            consultation = float(self.consultation_entry.get() or "0")
            medicine = float(self.medicine_entry.get() or "0")
            lab = float(self.lab_entry.get() or "0")
            other = float(self.other_entry.get() or "0")
            discount = float(self.discount_entry.get() or "0")
            tax_rate = float(self.tax_entry.get() or "0")

            subtotal = consultation + medicine + lab + other - discount
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount

            self.total_label.configure(text=f"₹{total:.2f}")

            # 🔄 Update QR if UPI is selected
            if self.payment_combo.get() == "UPI":
                self.on_payment_method_changed(None)

        except ValueError:
            self.total_label.configure(text="₹0.00")

    def generate_bill(self):
        if not self.patient_combo.get():
            MessageHelpers.show_error("Validation Error", "Please select a patient",parent=self.window)
            return

        try:
            # Extract patient ID
            patient_id = self.patient_combo.get().split(' - ')[0]

            # Get form data
            consultation_fee = float(self.consultation_entry.get() or "0")
            medicine_charges = float(self.medicine_entry.get() or "0")
            lab_charges = float(self.lab_entry.get() or "0")
            other_charges = float(self.other_entry.get() or "0")
            discount = float(self.discount_entry.get() or "0")
            tax_rate = float(self.tax_entry.get() or "0")

            payment_method = self.payment_combo.get()

            # Generate bill
            success, bill_id = self.bill_model.create_bill(
                patient_id, consultation_fee, medicine_charges,
                lab_charges, other_charges, discount, tax_rate,payment_method
            )

            if success:
                MessageHelpers.show_success("Success", f"Bill generated successfully! Bill ID: {bill_id}",parent=self.window)
                self.current_bill_id = bill_id
                self.load_bills()
            else:
                MessageHelpers.show_error("Error", bill_id,parent=self.window)  # Contains error message

        except ValueError:
            MessageHelpers.show_error("Validation Error", "Please enter valid amounts",parent=self.window)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate bill: {str(e)}",parent=self.window)

    def generate_pdf(self):
        if not self.patient_combo.get():
            MessageHelpers.show_error("Error", "Please select a patient and generate bill first",parent=self.window)
            return

        try:
            # Get patient info
            patient_id = self.patient_combo.get().split(' - ')[0]
            patient = self.patient_model.get_patient_by_id(patient_id)

            if not patient:
                MessageHelpers.show_error("Error", "Patient not found",parent=self.window)
                return

            # Prepare bill data
            consultation_fee = float(self.consultation_entry.get() or "0")
            medicine_charges = float(self.medicine_entry.get() or "0")
            lab_charges = float(self.lab_entry.get() or "0")
            other_charges = float(self.other_entry.get() or "0")
            discount = float(self.discount_entry.get() or "0")
            tax_rate = float(self.tax_entry.get() or "0")

            subtotal = consultation_fee + medicine_charges + lab_charges + other_charges - discount
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount

            bill_data = {
                'bill_id': getattr(self, 'current_bill_id', f'BILL{date.today().strftime("%Y%m%d")}'),
                'bill_date': date.today().strftime('%Y-%m-%d'),
                'consultation_fee': consultation_fee,
                'medicine_charges': medicine_charges,
                'lab_charges': lab_charges,
                'other_charges': other_charges,
                'discount': discount,
                'tax_amount': tax_amount,
                'total_amount': total_amount
            }

            # Create PDF
            pdf_generator = PDFGenerator(
                self.doctor_info['clinic_name'],
                self.doctor_info['doctor_name']
            )

            # Create downloads directory if it doesn't exist
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            filename = f"{downloads_dir}/bill_{patient_id}_{date.today().strftime('%Y%m%d')}.pdf"

            success, message = pdf_generator.generate_bill(patient, bill_data, filename)

            if success:
                MessageHelpers.show_success("Success", f"PDF generated successfully!\nSaved as: {filename}",parent=self.window)
            else:
                MessageHelpers.show_error("Error", message,parent=self.window)

        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to generate PDF: {str(e)}",parent=self.window)

    def clear_form(self):
        self.patient_combo.set("Select patient")
        self.consultation_entry.delete(0, 'end')
        self.consultation_entry.insert(0, "500.00")
        self.medicine_entry.delete(0, 'end')
        self.medicine_entry.insert(0, "0.00")
        self.lab_entry.delete(0, 'end')
        self.lab_entry.insert(0, "0.00")
        self.other_entry.delete(0, 'end')
        self.other_entry.insert(0, "0.00")
        self.discount_entry.delete(0, 'end')
        self.discount_entry.insert(0, "0.00")
        self.tax_entry.delete(0, 'end')
        self.tax_entry.insert(0, "18.00")
        self.payment_combo.set("Cash")
        self.calculate_total()

        if hasattr(self, 'current_bill_id'):
            del self.current_bill_id
