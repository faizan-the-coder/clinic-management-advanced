import customtkinter as ctk
from datetime import datetime, date
import re
from tkinter import messagebox


class UIHelpers:
    @staticmethod
    def create_rounded_frame(parent, corner_radius=10, **kwargs):
        frame = ctk.CTkFrame(parent, corner_radius=corner_radius, **kwargs)
        return frame

    @staticmethod
    def create_section_label(parent, text, text_color="#2c3e50", font=('Arial', 14, 'bold'), **kwargs):
        """A medium-bold label for section headers inside frames"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=font,  # now comes from parameter
            text_color=text_color,
            **kwargs
        )
        return label

    @staticmethod
    def create_styled_button(parent, text, command=None, width=150, height=35, **kwargs):
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=8,
            font=('Arial', 12, 'bold'),
            **kwargs
        )
        return button

    @staticmethod
    def create_styled_entry(parent, placeholder_text="", **kwargs):
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder_text,
            corner_radius=8,
            height=35,
            font=('Arial', 12),
            **kwargs
        )
        return entry

    @staticmethod
    def create_styled_textbox(parent, height=100, **kwargs):
        textbox = ctk.CTkTextbox(
            parent,
            height=height,
            corner_radius=8,
            font=('Arial', 12),
            **kwargs
        )
        return textbox

    @staticmethod
    def create_styled_combobox(parent, values, **kwargs):
        combobox = ctk.CTkComboBox(
            parent,
            values=values,
            corner_radius=8,
            height=35,
            font=('Arial', 12),
            **kwargs
        )
        return combobox

    @staticmethod
    def create_title_label(parent, text, **kwargs):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=('Arial', 20, 'bold'),
            **kwargs
        )
        return label

    @staticmethod
    def create_subtitle_label(parent, text, **kwargs):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=('Arial', 16, 'bold'),
            **kwargs
        )
        return label

    @staticmethod
    def create_normal_label(parent, text, **kwargs):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=('Arial', 12),
            **kwargs
        )
        return label


class ValidationHelpers:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone):
        pattern = r'^[+]?[0-9]{10,15}$'
        return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None

    @staticmethod
    def validate_required_fields(**fields):
        empty_fields = []
        for field_name, field_value in fields.items():
            if not field_value or field_value.strip() == "":
                empty_fields.append(field_name)
        return empty_fields

    @staticmethod
    def validate_password(password):
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        return True, "Valid password"


class DateHelpers:
    @staticmethod
    def string_to_date(date_string, format="%Y-%m-%d"):
        try:
            return datetime.strptime(date_string, format).date()
        except ValueError:
            return None

    @staticmethod
    def calculate_age(birth_date):
        if isinstance(birth_date, str):
            birth_date = DateHelpers.string_to_date(birth_date)

        if birth_date:
            today = date.today()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age
        return 0

    @staticmethod
    def get_time_slots():
        slots = []
        for hour in range(9, 18):  # 9 AM to 6 PM
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                slots.append(time_str)
        return slots


class MessageHelpers:
    @staticmethod
    def show_success(title, message, parent=None):
        messagebox.showinfo(title, message, parent=parent)

    @staticmethod
    def show_error(title, message, parent=None):
        messagebox.showerror(title, message, parent=parent)

    @staticmethod
    def show_warning(title, message, parent=None):
        messagebox.showwarning(title, message, parent=parent)

    @staticmethod
    def ask_confirmation(title, message, parent=None):
        return messagebox.askyesno(title, message, parent=parent)
