from decimal import Decimal
from .models import TaxYear, PAYEBracket, TaxRebate, MedicalCredit, TaxThreshold, UIFConfig, SDLConfig, ETIConfig

def calculate_paye(annual_taxable_income, age, tax_year, num_medical_dependents=0):
    """
    Calculates the annual PAYE based on SARS tax tables.
    """
    # 1. Find the applicable bracket
    brackets = PAYEBracket.objects.filter(tax_year=tax_year).order_by('from_amount')
    applicable_bracket = None
    for bracket in brackets:
        if annual_taxable_income >= bracket.from_amount:
            applicable_bracket = bracket
        else:
            break
    
    if not applicable_bracket:
        return Decimal('0.00')

    # 2. Calculate base tax
    tax = applicable_bracket.base_tax + (annual_taxable_income - applicable_bracket.from_amount) * applicable_bracket.rate

    # 3. Apply Rebates
    rebates = TaxRebate.objects.filter(tax_year=tax_year)
    total_rebate = Decimal('0.00')
    
    # Primary rebate for everyone
    primary = rebates.filter(type='primary').first()
    if primary:
        total_rebate += primary.amount
    
    # Secondary rebate for 65+
    if age >= 65:
        secondary = rebates.filter(type='secondary').first()
        if secondary:
            total_rebate += secondary.amount
            
    # Tertiary rebate for 75+
    if age >= 75:
        tertiary = rebates.filter(type='tertiary').first()
        if tertiary:
            total_rebate += tertiary.amount
            
    tax -= total_rebate

    # 4. Apply Medical Credits
    medical_credit_config = MedicalCredit.objects.filter(tax_year=tax_year).first()
    if medical_credit_config and num_medical_dependents > 0:
        total_medical_credit = medical_credit_config.first_dependent
        if num_medical_dependents >= 2:
            total_medical_credit += medical_credit_config.second_dependent
        if num_medical_dependents > 2:
            total_medical_credit += (num_medical_dependents - 2) * medical_credit_config.additional_dependents
        
        # Medical credits are monthly in SARS tables usually, but we need annual if we are doing annual tax
        # Actually SARS medical scheme fees tax credits are monthly.
        # Let's assume the values in DB are monthly and we annualize them.
        tax -= (total_medical_credit * 12)

    return max(tax, Decimal('0.00'))

def calculate_uif(gross_income, tax_year):
    """
    Calculates monthly UIF.
    """
    uif_config = UIFConfig.objects.filter(tax_year=tax_year).first()
    if not uif_config:
        return Decimal('0.00'), Decimal('0.00')
    
    # Employee UIF
    employee_uif = min(gross_income * uif_config.rate, uif_config.employee_cap)
    # Employer UIF
    employer_uif = min(gross_income * uif_config.rate, uif_config.employer_cap)
    
    return employee_uif, employer_uif

def calculate_sdl(gross_income, tax_year):
    """
    Calculates monthly SDL (Skills Development Levy).
    Employer contribution.
    """
    sdl_config = SDLConfig.objects.filter(tax_year=tax_year).first()
    if not sdl_config:
        return Decimal('0.00')
    
    # SARS SDL applies if annual payroll > annual_threshold (usually 500k)
    # Since we calculate per employee, we usually apply it if the organization is liable.
    # For this simplified engine, we'll apply it to all gross income if config exists.
    return gross_income * sdl_config.rate

def calculate_eti(remuneration, age, months_claimed, tax_year):
    """
    Calculates monthly ETI (Employment Tax Incentive).
    """
    if not (18 <= age <= 29):
        return Decimal('0.00')
    
    if months_claimed >= 24:
        return Decimal('0.00')
    
    phase = 1 if months_claimed < 12 else 2
    
    config = ETIConfig.objects.filter(
        tax_year=tax_year, 
        phase=phase,
        range_min__lte=remuneration,
        range_max__gte=remuneration
    ).first()
    
    if not config:
        return Decimal('0.00')
    
    eti_amount = config.fixed_amount
    eti_amount += remuneration * config.percentage
    if config.excess_threshold > 0 and remuneration > config.excess_threshold:
        eti_amount -= (remuneration - config.excess_threshold) * config.excess_percentage
        
    return max(eti_amount, Decimal('0.00'))

def run_payroll_for_employee(employee, payroll_run, earnings, deductions):
    """
    Calculates the payslip for a specific employee in a payroll run.
    earnings: list of (description, amount, is_taxable)
    deductions: list of (description, amount)
    """
    from .models import Payslip, PayslipItem
    from datetime import date
    
    # Calculate age
    today = date.today()
    age = today.year - employee.date_of_birth.year - ((today.month, today.day) < (employee.date_of_birth.month, employee.date_of_birth.day))
    
    gross_income = sum(item[1] for item in earnings)
    taxable_income = sum(item[1] for item in earnings if item[2])
    
    # For simplicity, we annualize current monthly taxable income
    annual_taxable_income = taxable_income * 12
    
    # PAYE
    annual_paye = calculate_paye(annual_taxable_income, age, payroll_run.tax_year, num_medical_dependents=employee.medical_dependents)
    monthly_paye = annual_paye / 12
    
    # UIF
    employee_uif, employer_uif = calculate_uif(gross_income, payroll_run.tax_year)
    
    # ETI
    eti = calculate_eti(gross_income, age, employee.eti_months_claimed, payroll_run.tax_year)

    # SDL
    sdl = calculate_sdl(gross_income, payroll_run.tax_year)

    total_deductions = sum(item[1] for item in deductions) + monthly_paye + employee_uif
    net_pay = gross_income - total_deductions
    
    payslip = Payslip.objects.create(
        payroll_run=payroll_run,
        employee=employee,
        gross_income=gross_income,
        taxable_income=taxable_income,
        total_deductions=total_deductions,
        net_pay=net_pay,
        paye=monthly_paye,
        uif=employee_uif,
        sdl=sdl,
        eti=eti
    )
    
    for desc, amount, taxable in earnings:
        PayslipItem.objects.create(
            payslip=payslip,
            description=desc,
            item_type='earning',
            amount=amount,
            is_taxable=taxable
        )
        
    for desc, amount in deductions:
        PayslipItem.objects.create(
            payslip=payslip,
            description=desc,
            item_type='deduction',
            amount=amount,
            is_taxable=False
        )
    
    # Add PAYE and UIF as items too? The architecture says they are fields on Payslip, 
    # but PayslipItem can also store them for detail. 
    # Let's just keep them in fields for now as per schema.
    
    return payslip
