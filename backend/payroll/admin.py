from django.contrib import admin
from .models import (
    Organization, Employee, TaxYear, PAYEBracket, TaxRebate,
    MedicalCredit, TaxThreshold, UIFConfig, PayrollRun, Payslip, PayslipItem
)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_no', 'tax_no')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_code', 'organization', 'status')
    list_filter = ('organization', 'status')
    search_fields = ('first_name', 'last_name', 'employee_code')

@admin.register(TaxYear)
class TaxYearAdmin(admin.ModelAdmin):
    list_display = ('label', 'start_date', 'end_date')

@admin.register(PAYEBracket)
class PAYEBracketAdmin(admin.ModelAdmin):
    list_display = ('tax_year', 'from_amount', 'base_tax', 'rate')
    list_filter = ('tax_year',)

@admin.register(TaxRebate)
class TaxRebateAdmin(admin.ModelAdmin):
    list_display = ('tax_year', 'type', 'amount')
    list_filter = ('tax_year',)

@admin.register(MedicalCredit)
class MedicalCreditAdmin(admin.ModelAdmin):
    list_display = ('tax_year', 'first_dependent', 'second_dependent', 'additional_dependents')

@admin.register(TaxThreshold)
class TaxThresholdAdmin(admin.ModelAdmin):
    list_display = ('tax_year', 'age_under_65', 'age_65_to_75', 'age_75_over')

@admin.register(UIFConfig)
class UIFConfigAdmin(admin.ModelAdmin):
    list_display = ('tax_year', 'rate', 'employee_cap', 'employer_cap')

class PayslipItemInline(admin.TabularInline):
    model = PayslipItem
    extra = 1

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ('organization', 'tax_year', 'period_month', 'period_year', 'status')
    list_filter = ('organization', 'tax_year', 'status')

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll_run', 'gross_income', 'net_pay')
    inlines = [PayslipItemInline]
    list_filter = ('payroll_run',)
