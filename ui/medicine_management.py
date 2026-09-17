import customtkinter as ctk
from database.models import MedicineModel
from utils.helpers import UIHelpers, MessageHelpers, DateHelpers
from config import UI_COLORS
from tkcalendar import DateEntry
from datetime import date
from datetime import datetime


class MedicineManagementWindow:
    def __init__(self, doctor_info):
        self.doctor_info = doctor_info
        self.medicine_model = MedicineModel()
        self.current_medicine = None

        # Create window
        self.window = ctk.CTkToplevel()
        self.window.title("Medicine Management")
        self.window.geometry("900x600+10+10")
        self.window.transient()
        self.window.grab_set()

        self.setup_ui()
        self.load_medicines()

    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Left panel - Medicine form
        self.setup_medicine_form(main_frame)

        # Right panel - Medicine list
        self.setup_medicine_list(main_frame)

    def setup_medicine_form(self, parent):
        # Form frame
        form_frame = UIHelpers.create_rounded_frame(
            parent,
            fg_color=UI_COLORS['card'],
            corner_radius=15,
            width=400
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_propagate(False)

        # Header
        header_label = UIHelpers.create_subtitle_label(
            form_frame,
            "Medicine Information",
            text_color=UI_COLORS['primary']
        )
        header_label.grid(row=0, column=0, columnspan=2, pady=15, sticky="w", padx=20)

        # Medicine ID (read-only)
        UIHelpers.create_normal_label(form_frame, "Medicine ID:", text_color=UI_COLORS['text']).grid(
            row=1, column=0, sticky="w", padx=20, pady=5
        )
        self.medicine_id_label = UIHelpers.create_normal_label(
            form_frame, "Auto-generated", text_color=UI_COLORS['text_secondary']
        )
        self.medicine_id_label.grid(row=1, column=1, sticky="w", padx=20, pady=5)

        # Name
        UIHelpers.create_normal_label(form_frame, "Name*:", text_color=UI_COLORS['text']).grid(
            row=2, column=0, sticky="w", padx=20, pady=5
        )
        self.name_entry = UIHelpers.create_styled_entry(form_frame, placeholder_text="Medicine name", width=250)
        self.name_entry.grid(row=2, column=1, sticky="w", padx=20, pady=5)

        # Category
        UIHelpers.create_normal_label(form_frame, "Category:", text_color=UI_COLORS['text']).grid(
            row=3, column=0, sticky="w", padx=20, pady=5
        )
        categories = ["Tablet", "Capsule", "Syrup", "Injection", "Cream", "Drops", "Other"]
        self.category_combo = UIHelpers.create_styled_combobox(form_frame, values=categories, width=150)
        self.category_combo.grid(row=3, column=1, sticky="w", padx=20, pady=5)

        # Manufacturer
        UIHelpers.create_normal_label(form_frame, "Manufacturer:", text_color=UI_COLORS['text']).grid(
            row=4, column=0, sticky="w", padx=20, pady=5
        )
        self.manufacturer_entry = UIHelpers.create_styled_entry(form_frame, placeholder_text="Manufacturer", width=250)
        self.manufacturer_entry.grid(row=4, column=1, sticky="w", padx=20, pady=5)

        # Batch No
        UIHelpers.create_normal_label(form_frame, "Batch No:", text_color=UI_COLORS['text']).grid(
            row=5, column=0, sticky="w", padx=20, pady=5
        )
        self.batch_entry = UIHelpers.create_styled_entry(form_frame, placeholder_text="Batch number", width=150)
        self.batch_entry.grid(row=5, column=1, sticky="w", padx=20, pady=5)

        # Expiry Date
        UIHelpers.create_normal_label(form_frame, "Expiry Date:", text_color=UI_COLORS['text']).grid(
            row=6, column=0, sticky="w", padx=20, pady=5
        )
        self.expiry_date = DateEntry(
            form_frame,
            width=12,
            font=('arial', 18),
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            mindate=date.today()
        )
        self.expiry_date.grid(row=6, column=1, sticky="w", padx=30, pady=5)

        # Stock Quantity
        UIHelpers.create_normal_label(form_frame, "Stock Qty:", text_color=UI_COLORS['text']).grid(
            row=7, column=0, sticky="w", padx=20, pady=5
        )
        self.stock_entry = UIHelpers.create_styled_entry(form_frame, placeholder_text="0", width=100)
        self.stock_entry.grid(row=7, column=1, sticky="w", padx=20, pady=5)

        # Price
        UIHelpers.create_normal_label(form_frame, "Price (₹):", text_color=UI_COLORS['text']).grid(
            row=8, column=0, sticky="w", padx=20, pady=5
        )
        self.price_entry = UIHelpers.create_styled_entry(form_frame, placeholder_text="0.00", width=100)
        self.price_entry.grid(row=8, column=1, sticky="w", padx=20, pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        self.save_btn = UIHelpers.create_styled_button(
            button_frame,
            "Add Medicine",
            command=self.save_medicine,
            fg_color=UI_COLORS['primary'],
            hover_color=UI_COLORS['hover'],
            width=120
        )
        self.save_btn.grid(row=0, column=0, padx=5)

        self.update_btn = UIHelpers.create_styled_button(
            button_frame,
            "Update",
            command=self.update_medicine,
            fg_color=UI_COLORS['success'],
            hover_color="#D68910",
            width=80
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

    def setup_medicine_list(self, parent):
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
            "Medicine Inventory",
            text_color=UI_COLORS['primary']
        )
        header_label.grid(row=0, column=0, pady=15, sticky="w", padx=20)

        # Filter buttons
        filter_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))

        all_btn = UIHelpers.create_styled_button(
            filter_frame,
            "All Medicines",
            command=self.load_medicines,
            width=100,
            height=30
        )
        all_btn.pack(side="left", padx=(0, 10))

        low_stock_btn = UIHelpers.create_styled_button(
            filter_frame,
            "Low Stock",
            command=self.load_low_stock,
            fg_color=UI_COLORS['danger'],
            hover_color="#C0392B",
            width=100,
            height=30
        )
        low_stock_btn.pack(side="left")

        expiry_btn = UIHelpers.create_styled_button(
            filter_frame,
            "Expiry Medicines",
            command=self.load_expiry_medicines,
            fg_color=UI_COLORS["warning"],
            hover_color="#FFC107",
            width=130,
            height=30,
        )
        expiry_btn.pack(side="left", padx=10)

        # Medicine list
        self.medicine_listbox = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=UI_COLORS['background']
        )
        self.medicine_listbox.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

    def get_days_until_expiry(self, expiry_date_value):
        # Convert to date object if needed
        if isinstance(expiry_date_value, str):
            expiry_date = datetime.strptime(expiry_date_value, "%Y-%m-%d").date()
        elif isinstance(expiry_date_value, datetime):
            expiry_date = expiry_date_value.date()
        else:
            expiry_date = expiry_date_value

        today = date.today()
        days_left = (expiry_date - today).days

        if days_left < 0:
            return f"Expired ({abs(days_left)} days ago)"
        elif days_left == 0:
            return "Expires today"
        else:
            return f"Expires in {days_left} days"

    def load_expiry_medicines(self):
        try:
            medicines = self.medicine_model.get_expiry_medicines(30)
            for med in medicines:
                med['days_left'] = self.get_days_until_expiry(med['expiry_date'])
            self.display_medicines(medicines)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to load expiry medicines: {str(e)}", parent=self.window)

    def load_medicines(self):
        try:
            medicines = self.medicine_model.get_all_medicines()
            self.display_medicines(medicines)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to load medicines: {str(e)}", parent=self.window)

    def load_low_stock(self):
        try:
            medicines = self.medicine_model.get_low_stock_medicines(10)
            self.display_medicines(medicines)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to load low stock medicines: {str(e)}", parent=self.window)

    def display_medicines(self, medicines):
        # Clear existing medicines
        for widget in self.medicine_listbox.winfo_children():
            widget.destroy()

        if not medicines:
            no_med_label = UIHelpers.create_normal_label(
                self.medicine_listbox,
                "No medicines found",
                text_color=UI_COLORS['text_secondary']
            )
            no_med_label.pack(pady=20)
            return

        # Display medicines
        for med in medicines:
            med_frame = UIHelpers.create_rounded_frame(
                self.medicine_listbox,
                fg_color=UI_COLORS['card'],
                corner_radius=8,
                height=80
            )
            med_frame.pack(fill="x", pady=2)
            med_frame.grid_columnconfigure(1, weight=1)
            med_frame.grid_propagate(False)

            # Medicine ID
            id_label = UIHelpers.create_normal_label(
                med_frame,
                med['medicine_id'],
                text_color=UI_COLORS['primary']
            )
            id_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Medicine Name
            name_label = UIHelpers.create_normal_label(
                med_frame,
                med['name'],
                text_color=UI_COLORS['text']
            )
            name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            # Category and Stock
            info_label = UIHelpers.create_normal_label(
                med_frame,
                f"{med['category']} | Stock: {med['stock_quantity']}",
                text_color=UI_COLORS['text_secondary']
            )
            info_label.grid(row=1, column=1, padx=10, pady=(0, 5), sticky="w")

            # Price
            price_label = UIHelpers.create_normal_label(
                med_frame,
                f"₹{med['price']:.2f}",
                text_color=UI_COLORS['success']
            )
            price_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

            # Show expiry info if available
            # Show expiry info if available
            if 'days_left' in med:
                expiry_text = med['days_left']  # Already a full readable string
                # Choose color dynamically
                if expiry_text.startswith("Expired"):
                    color = UI_COLORS['danger']
                elif "today" in expiry_text:
                    color = UI_COLORS['warning']
                else:
                    color = UI_COLORS['success']

                expiry_label = UIHelpers.create_normal_label(
                    med_frame,
                    expiry_text,
                    text_color=color
                )
                expiry_label.grid(row=1, column=2, padx=10, pady=(0, 5), sticky="e")

            # Stock warning
            elif med['stock_quantity'] <= 10:
                warning_label = UIHelpers.create_normal_label(
                    med_frame,
                    "LOW STOCK!",
                    text_color=UI_COLORS['danger']
                )
                warning_label.grid(row=1, column=2, padx=10, pady=(0, 5), sticky="e")

            # Make clickable
            for widget in [med_frame, id_label, name_label, info_label, price_label]:
                widget.bind("<Button-1>", lambda e, m=med: self.select_medicine(m))
                widget.configure(cursor="hand2")

    def select_medicine(self, medicine):
        self.current_medicine = medicine
        self.populate_form(medicine)

    def populate_form(self, medicine):
        # Clear form first
        self.clear_form()

        # Populate fields
        self.medicine_id_label.configure(text=medicine['medicine_id'])
        self.name_entry.insert(0, medicine['name'])
        self.category_combo.set(medicine['category'] or "")
        self.manufacturer_entry.insert(0, medicine['manufacturer'] or "")
        self.batch_entry.insert(0, medicine['batch_no'] or "")

        # Set expiry date
        if medicine['expiry_date']:
            try:
                if isinstance(medicine['expiry_date'], str):
                    exp_date = DateHelpers.string_to_date(medicine['expiry_date'])
                else:
                    exp_date = medicine['expiry_date']
                self.expiry_date.set_date(exp_date)
            except:
                pass

        self.stock_entry.insert(0, str(medicine['stock_quantity']))
        self.price_entry.insert(0, str(medicine['price']))

        # Show update button, hide save button
        self.save_btn.grid_remove()
        self.update_btn.grid()

    def clear_form(self):

        self.medicine_id_label.configure(text="Auto-generated")
        self.name_entry.delete(0, 'end')
        self.name_entry.configure(placeholder_text="Medicine name")
        self.category_combo.set("Tablet")
        self.manufacturer_entry.delete(0, 'end')
        self.manufacturer_entry.configure(placeholder_text="Manufacturer")
        self.batch_entry.delete(0, 'end')
        self.batch_entry.configure(placeholder_text="Batch number")
        self.expiry_date.set_date(date.today())
        self.stock_entry.delete(0, 'end')
        self.stock_entry.configure(placeholder_text="0")
        self.price_entry.delete(0, 'end')
        self.price_entry.configure(placeholder_text="0.00")

        # Show save button, hide update button
        self.update_btn.grid_remove()
        self.save_btn.grid()

    def save_medicine(self):
        # Validate required fields
        if not self.name_entry.get().strip():
            MessageHelpers.show_error("Validation Error", "Medicine name is required", parent=self.window)
            return

        try:
            # Get form data
            name = self.name_entry.get().strip()
            category = self.category_combo.get().strip()
            manufacturer = self.manufacturer_entry.get().strip()
            batch_no = self.batch_entry.get().strip()
            expiry_date = self.expiry_date.get_date()
            stock_quantity = int(self.stock_entry.get().strip() or "0")
            price = float(self.price_entry.get().strip() or "0.00")

            # Add medicine
            success, medicine_id = self.medicine_model.add_medicine(
                name, category, manufacturer, batch_no, expiry_date, stock_quantity, price
            )

            if success:
                MessageHelpers.show_success("Success", f"Medicine added successfully! ID: {medicine_id}",
                                            parent=self.window)
                self.clear_form()
                self.load_medicines()
            else:
                MessageHelpers.show_error("Error", medicine_id, parent=self.window)  # Contains error message

        except ValueError as e:
            MessageHelpers.show_error("Validation Error", "Please enter valid numbers for stock and price",
                                      parent=self.window)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to save medicine: {str(e)}", parent=self.window)

    def update_medicine(self):
        if not self.current_medicine:
            MessageHelpers.show_error("No Selection", "Please select a medicine to update", parent=self.window)
            return

        # Validate required fields
        name = self.name_entry.get().strip()
        if not name:
            MessageHelpers.show_error("Validation Error", "Medicine name is required", parent=self.window)
            return

        try:
            medicine_id = self.current_medicine['medicine_id']
            category = self.category_combo.get().strip()
            manufacturer = self.manufacturer_entry.get().strip()
            batch_no = self.batch_entry.get().strip()
            expiry_date = self.expiry_date.get_date()
            stock_quantity = int(self.stock_entry.get().strip() or "0")
            price = float(self.price_entry.get().strip() or "0.00")

            # Call model update
            success, msg = self.medicine_model.update_medicine(
                medicine_id,
                name,
                category,
                manufacturer,
                batch_no,
                expiry_date,
                stock_quantity,
                price
            )

            if success:
                MessageHelpers.show_success("Success", f"Medicine updated successfully! ID: {medicine_id}",
                                            parent=self.window)
                self.clear_form()
                self.load_medicines()
            else:
                MessageHelpers.show_error("Error", msg, parent=self.window)  # msg contains error description

        except ValueError:
            MessageHelpers.show_error("Validation Error", "Please enter valid numbers for stock and price",
                                      parent=self.window)
        except Exception as e:
            MessageHelpers.show_error("Error", f"Failed to update medicine: {str(e)}", parent=self.window)
