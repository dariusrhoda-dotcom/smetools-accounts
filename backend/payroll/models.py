from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255)
    registration_no = models.CharField(max_length=100, blank=True, null=True)
    tax_no = models.CharField(max_length=100, blank=True, null=True)
    uif_no = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='employees')
    employee_code = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=13, blank=True, null=True)
    tax_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    join_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    bank_details = models.JSONField(blank=True, null=True)
    tax_directive_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    eti_months_claimed = models.IntegerField(default=0)
    medical_dependents = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_code})"

class TaxYear(models.Model):
    label = models.CharField(max_length=20)  # e.g., "2023/2024"
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.label

class PAYEBracket(models.Model):
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name='paye_brackets')
    from_amount = models.DecimalField(max_digits=12, decimal_places=2)
    base_tax = models.DecimalField(max_digits=12, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage as decimal, e.g., 0.18

    class Meta:
        ordering = ['from_amount']

class TaxRebate(models.Model):
    REBATE_TYPES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary (65+)'),
        ('tertiary', 'Tertiary (75+)'),
    ]
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name='tax_rebates')
    type = models.CharField(max_length=20, choices=REBATE_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

class MedicalCredit(models.Model):
    tax_year = models.OneToOneField(TaxYear, on_delete=models.CASCADE, related_name='medical_credit')
    first_dependent = models.DecimalField(max_digits=10, decimal_places=2)
    second_dependent = models.DecimalField(max_digits=10, decimal_places=2)
    additional_dependents = models.DecimalField(max_digits=10, decimal_places=2)

class TaxThreshold(models.Model):
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name='tax_thresholds')
    age_under_65 = models.DecimalField(max_digits=12, decimal_places=2)
    age_65_to_75 = models.DecimalField(max_digits=12, decimal_places=2)
    age_75_over = models.DecimalField(max_digits=12, decimal_places=2)

class UIFConfig(models.Model):
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name='uif_config')
    rate = models.DecimalField(max_digits=5, decimal_places=4)  # e.g., 0.01
    employee_cap = models.DecimalField(max_digits=10, decimal_places=2)
    employer_cap = models.DecimalField(max_digits=10, decimal_places=2)

class SDLConfig(models.Model):
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name='sdl_config')
    rate = models.DecimalField(max_digits=5, decimal_places=4) # e.g. 0.01
    annual_threshold = models.DecimalField(max_digits=12, decimal_places=2)

class ETIConfig(models.Model):
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE, related_name='eti_configs')
    phase = models.IntegerField() # 1 or 2
    range_min = models.DecimalField(max_digits=12, decimal_places=2)
    range_max = models.DecimalField(max_digits=12, decimal_places=2)
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    excess_percentage = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    excess_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class PayrollRun(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('finalized', 'Finalized'),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='payroll_runs')
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    period_month = models.IntegerField()
    period_year = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} - {self.period_year}/{self.period_month}"

class Payslip(models.Model):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    gross_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taxable_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paye = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    uif = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sdl = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    eti = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pdf_storage_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Payslip {self.employee} - {self.payroll_run}"

class PayslipItem(models.Model):
    ITEM_TYPES = [
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
        ('employer_contribution', 'Employer Contribution'),
    ]
    payslip = models.ForeignKey(Payslip, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    item_type = models.CharField(max_length=30, choices=ITEM_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_taxable = models.BooleanField(default=True)
