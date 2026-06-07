export interface Organization {
  id: number;
  name: string;
  registration_no?: string;
  tax_no?: string;
  uif_no?: string;
  address?: string;
}

export interface Employee {
  id: number;
  organization: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  id_number?: string;
  tax_number?: string;
  date_of_birth?: string;
  join_date: string;
  status: 'active' | 'terminated' | 'on_leave';
  bank_details?: any;
  tax_directive_rate?: number;
}

export interface TaxYear {
  id: number;
  label: string;
  start_date: string;
  end_date: string;
}

export interface PayrollRun {
  id: number;
  organization: number;
  tax_year: number;
  tax_year_label?: string;
  period_month: number;
  period_year: number;
  status: 'draft' | 'finalized';
  created_at: string;
}

export interface Payslip {
  id: number;
  payroll_run: number;
  employee: number;
  employee_name?: string;
  gross_income: string;
  taxable_income: string;
  total_deductions: string;
  net_pay: string;
  paye: string;
  uif: string;
  sdl: string;
  pdf_storage_path?: string;
}

export interface PayslipItem {
  id: number;
  payslip: number;
  description: string;
  item_type: 'earning' | 'deduction' | 'employer_contribution';
  amount: string;
  is_taxable: boolean;
}
