from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import date
import os

class PDFGenerator:
    def __init__(self, clinic_name, doctor_name):
        self.clinic_name = clinic_name
        self.doctor_name = doctor_name
        self.styles = getSampleStyleSheet()

        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            alignment=TA_LEFT,
            spaceAfter=10
        )

        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=6
        )

    def generate_prescription(self, patient_info, prescription_data, items, filename):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []

            # Clinic Header
            clinic_header = Paragraph(f"<b>{self.clinic_name}</b>", self.title_style)
            doctor_info = Paragraph(f"Dr. {self.doctor_name}", self.styles['Heading3'])
            story.extend([clinic_header, doctor_info, Spacer(1, 20)])

            # Prescription Title
            title = Paragraph("<b>PRESCRIPTION</b>", self.header_style)
            story.append(title)
            story.append(Spacer(1, 10))

            # Patient Information
            patient_data = [
                ['Patient ID:', patient_info.get('patient_id', 'N/A')],
                ['Name:', patient_info.get('name', 'N/A')],
                ['Age/Gender:', f"{patient_info.get('age', 'N/A')} / {patient_info.get('gender', 'N/A')}"],
                ['Date:', prescription_data.get('prescription_date', date.today().strftime('%Y-%m-%d'))]
            ]

            patient_table = Table(patient_data, colWidths=[1.5*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))

            story.append(patient_table)
            story.append(Spacer(1, 20))

            # Diagnosis
            if prescription_data.get('diagnosis'):
                diagnosis_title = Paragraph("<b>Diagnosis:</b>", self.header_style)
                diagnosis_text = Paragraph(prescription_data['diagnosis'], self.normal_style)
                story.extend([diagnosis_title, diagnosis_text, Spacer(1, 15)])

            # Medications
            medications_title = Paragraph("<b>Rx:</b>", self.header_style)
            story.append(medications_title)

            med_data = [['Medicine', 'Dosage', 'Duration', 'Remarks']]
            for item in items:
                print(item)
                med_data.append([
                    item.get('medicine', ''),
                    item.get('dosage', ''),
                    item.get('duration', ''),
                    item.get('remarks', '')
                ])

            med_table = Table(med_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
            med_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(med_table)
            story.append(Spacer(1, 30))

            # Doctor Signature
            signature = Paragraph(f"<br/><br/>Dr. {self.doctor_name}<br/>{self.clinic_name}", 
                                 ParagraphStyle('Signature', parent=self.styles['Normal'], 
                                              fontSize=11, alignment=TA_RIGHT))
            story.append(signature)

            doc.build(story)
            return True, f"Prescription saved as {filename}"

        except Exception as e:
            return False, f"Error generating prescription: {str(e)}"

    def generate_bill(self, patient_info, bill_data, filename):
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []

            # Clinic Header
            clinic_header = Paragraph(f"<b>{self.clinic_name}</b>", self.title_style)
            doctor_info = Paragraph(f"Dr. {self.doctor_name}", self.styles['Heading3'])
            story.extend([clinic_header, doctor_info, Spacer(1, 20)])

            # Bill Title
            title = Paragraph("<b>MEDICAL BILL</b>", self.header_style)
            story.append(title)
            story.append(Spacer(1, 10))

            # Bill and Patient Information
            info_data = [
                ['Bill ID:', bill_data.get('bill_id', 'N/A'), 'Patient ID:', patient_info.get('patient_id', 'N/A')],
                ['Date:', bill_data.get('bill_date', date.today().strftime('%Y-%m-%d')), 'Patient Name:', patient_info.get('name', 'N/A')],
                ['', '', 'Phone:', patient_info.get('phone', 'N/A')]
            ]

            info_table = Table(info_data, colWidths=[1*inch, 2*inch, 1*inch, 2*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))

            story.append(info_table)
            story.append(Spacer(1, 20))

            # Bill Details
            bill_details = [
                ['Description', 'Amount'],
                ['Consultation Fee', f"Rs. {bill_data.get('consultation_fee', 0):.2f}"],
                ['Medicine Charges', f"Rs. {bill_data.get('medicine_charges', 0):.2f}"],
                ['Lab Charges', f"Rs. {bill_data.get('lab_charges', 0):.2f}"],
                ['Other Charges', f"Rs. {bill_data.get('other_charges', 0):.2f}"],
                ['Discount', f"-Rs. {bill_data.get('discount', 0):.2f}"],
                ['Tax', f"Rs. {bill_data.get('tax_amount', 0):.2f}"],
                ['Total Amount', f"Rs. {bill_data.get('total_amount', 0):.2f}"]
            ]

            bill_table = Table(bill_details, colWidths=[4*inch, 2*inch])
            bill_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(bill_table)
            story.append(Spacer(1, 30))

            # Footer
            footer = Paragraph("Thank you for choosing our services!", 
                             ParagraphStyle('Footer', parent=self.styles['Normal'], 
                                          fontSize=11, alignment=TA_CENTER))
            story.append(footer)

            doc.build(story)
            return True, f"Bill saved as {filename}"

        except Exception as e:
            return False, f"Error generating bill: {str(e)}"

    def generate_report(self, title, data, headers, filename):
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []

            # Clinic Header
            clinic_header = Paragraph(f"<b>{self.clinic_name}</b>", self.title_style)
            doctor_info = Paragraph(f"Dr. {self.doctor_name}", self.styles['Heading3'])
            story.extend([clinic_header, doctor_info, Spacer(1, 20)])

            # Report Title
            report_title = Paragraph(f"<b>{title}</b>", self.header_style)
            story.append(report_title)

            # Date
            date_para = Paragraph(f"Generated on: {date.today().strftime('%B %d, %Y')}", self.normal_style)
            story.append(date_para)
            story.append(Spacer(1, 15))

            # Data Table
            table_data = [headers] + data

            # Wrap data cells with Paragraph for text wrapping
            wrapped_data = []
            for row in [headers] + data:
                wrapped_row = []
                for cell in row:
                    wrapped_cell = Paragraph(str(cell), self.normal_style)
                    wrapped_row.append(wrapped_cell)
                wrapped_data.append(wrapped_row)

            # Calculate column widths
            col_width = 7.5 * inch / len(headers)
            col_widths = [col_width] * len(headers)

            table = Table(wrapped_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))

            story.append(table)

            doc.build(story)
            return True, f"Report saved as {filename}"

        except Exception as e:
            return False, f"Error generating report: {str(e)}"
