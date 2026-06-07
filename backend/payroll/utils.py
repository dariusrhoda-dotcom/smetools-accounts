import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import date

def generate_payslip_pdf(payslip):
    """
    Generates a PDF for a given payslip and returns the path to the saved file.
    """
    earnings = payslip.items.filter(item_type='earning')
    deductions = payslip.items.filter(item_type='deduction')
    
    context = {
        'payslip': payslip,
        'employee': payslip.employee,
        'organization': payslip.payroll_run.organization,
        'payroll_run': payslip.payroll_run,
        'earnings': earnings,
        'deductions': deductions,
        'today': date.today(),
    }
    
    html_string = render_to_string('payroll/payslip_template.html', context)
    
    # Define file path
    filename = f"payslip_{payslip.employee.employee_code}_{payslip.payroll_run.period_year}_{payslip.payroll_run.period_month}.pdf"
    output_dir = os.path.join(settings.MEDIA_ROOT, 'payslips')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    # Generate PDF
    HTML(string=html_string).write_pdf(file_path)
    
    # Update payslip with storage path
    payslip.pdf_storage_path = os.path.join('payslips', filename)
    payslip.save()
    
    return file_path
