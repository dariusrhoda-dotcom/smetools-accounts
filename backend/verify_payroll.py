import os
import django
from decimal import Decimal
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smetools_payroll_backend.settings')
django.setup()

from payroll.models import Organization, Employee, TaxYear, PayrollRun, PAYEBracket, TaxRebate, MedicalCredit, UIFConfig, ETIConfig
from payroll.engine import run_payroll_for_employee

def setup_test_data():
    # 1. Clear existing test data if any
    Organization.objects.filter(name="Verification Org").delete()
    TaxYear.objects.filter(label="2024/2025").delete()

    # 2. Create Tax Year 2024/2025
    ty = TaxYear.objects.create(
        label="2024/2025",
        start_date=date(2024, 3, 1),
        end_date=date(2025, 2, 28)
    )

    # 3. Create PAYE Brackets (SARS 2025)
    PAYEBracket.objects.create(tax_year=ty, from_amount=Decimal('0'), base_tax=Decimal('0'), rate=Decimal('0.18'))
    PAYEBracket.objects.create(tax_year=ty, from_amount=Decimal('237101'), base_tax=Decimal('42678'), rate=Decimal('0.26'))

    # 4. Create Rebates (SARS 2025)
    TaxRebate.objects.create(tax_year=ty, type='primary', amount=Decimal('17235'))

    # 5. Create Medical Credits (SARS 2025 - Monthly)
    MedicalCredit.objects.create(
        tax_year=ty,
        first_dependent=Decimal('364'),
        second_dependent=Decimal('364'),
        additional_dependents=Decimal('246')
    )

    # 6. Create UIF Config
    UIFConfig.objects.create(
        tax_year=ty,
        rate=Decimal('0.01'),
        employee_cap=Decimal('177.12'),
        employer_cap=Decimal('177.12')
    )

    # 7. Create Org and Employee
    org = Organization.objects.create(name="Verification Org")
    emp = Employee.objects.create(
        organization=org,
        employee_code="VERIF001",
        first_name="Verif",
        last_name="Test",
        id_number="9501015000081",
        date_of_birth=date(1995, 1, 1),
        join_date=date(2022, 1, 1),
        medical_dependents=2,
        eti_months_claimed=0
    )

    # 8. Create Payroll Run
    pr = PayrollRun.objects.create(
        organization=org,
        tax_year=ty,
        period_month=4,
        period_year=2024
    )

    return emp, pr

def test_calculation():
    emp, pr = setup_test_data()
    
    # Monthly Salary: R30,000
    earnings = [("Basic Salary", Decimal("30000.00"), True)]
    deductions = []
    
    payslip = run_payroll_for_employee(emp, pr, earnings, deductions)
    
    print(f"--- Verification Results ---")
    print(f"Employee: {emp.first_name} {emp.last_name}")
    print(f"Gross Income: R{payslip.gross_income}")
    print(f"Taxable Income: R{payslip.taxable_income}")
    print(f"PAYE: R{payslip.paye}")
    print(f"UIF: R{payslip.uif}")
    print(f"Net Pay: R{payslip.net_pay}")
    
    # Validation logic
    # Annual: 30,000 * 12 = 360,000
    # Tax on 360,000: 42,678 + (360,000 - 237,100) * 0.26 = 42,678 + 31,954 = 74,632
    # Less Primary Rebate: 74,632 - 17,235 = 57,397
    # Less Medical Credits (2 dependents): (364 + 364) * 12 = 728 * 12 = 8,736
    # Total Annual PAYE: 57,397 - 8,736 = 48,661
    # Monthly PAYE: 48,661 / 12 = 4,055.08
    
    expected_paye = Decimal('4055.08')
    diff = abs(payslip.paye - expected_paye)
    
    if diff < 1:
        print("✓ PAYE Calculation Verified")
    else:
        print(f"✗ PAYE Calculation Discrepancy: Expected ~{expected_paye}, Got {payslip.paye}")

    # Test PDF Generation
    print("Testing PDF Generation...")
    from payroll.utils import generate_payslip_pdf
    try:
        pdf_path = generate_payslip_pdf(payslip)
        if os.path.exists(pdf_path):
            print(f"✓ PDF Generated Successfully at: {pdf_path}")
        else:
            print("✗ PDF File not found after generation")
    except Exception as e:
        print(f"✗ PDF Generation Failed: {e}")

if __name__ == "__main__":
    test_calculation()
