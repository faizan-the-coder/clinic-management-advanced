# Clinic Management System (Advanced)

## Overview

Modular clinic application covering appointments, patients, doctors, medicines, billing, prescriptions and analytics.

## Project Timeline

Development period: Approximately 2025 (source files dated 2025-10; timeline approximate, no Git history).

## Key Features

- Appointment, patient and doctor management
- Medicine stock with billing and prescriptions
- Reports and analytics dashboard
- PDF generation for records

## Technologies

Python, CustomTkinter, MySQL, Matplotlib, ReportLab, qrcode, tkcalendar, bcrypt

## Development

Development: AI-assisted. Requirements, database schema, UI direction, customization, debugging, testing and integration were done by the author; AI tooling assisted with scaffolding and boilerplate.

## Screenshots

![Clinic dashboard](screenshots/01-clinic-dashboard.png)
![Patient management](screenshots/02-patient-management.png)
![Billing and invoice](screenshots/03-billing-and-invoice.png)
![Doctor registration](screenshots/04-doctor-registration.png)

## Requirements

Python 3.10 or newer recommended.

## Installation

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and set your local MySQL values.

## Database Setup

Create the MySQL database, then launch the app to initialize tables. Seed only fictional demo patients (for example John Doe).

## Running the Application

```
python main.py
```

## Demo Credentials

Fictional demo accounts only. No real patient data is included.

## Limitations

- Desktop-only Tkinter UI; no web or mobile client.
- Designed for single-store / single-office use; not load-tested for multi-user concurrency.

## Future Improvements

- Appointment reminders and web portal.
