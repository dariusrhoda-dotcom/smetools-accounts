import axios from 'axios';
import { Employee, PayrollRun, Payslip, TaxYear, Organization } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const organizationService = {
  getAll: () => api.get<Organization[]>('/organizations/'),
  getById: (id: number) => api.get<Organization>(`/organizations/${id}/`),
  getStats: (id: number) => api.get<{
    employee_count: number;
    total_paye_mtd: number;
    total_net_mtd: number;
    recent_runs: Array<{
      id: number;
      period: string;
      status: string;
      employee_count: number;
    }>;
  }>(`/organizations/${id}/stats/`),
};

export const employeeService = {
  getAll: (orgId?: number) => api.get<Employee[]>('/employees/', { params: { organization_id: orgId } }),
  getById: (id: number) => api.get<Employee>(`/employees/${id}/`),
  create: (data: Partial<Employee>) => api.post<Employee>('/employees/', data),
  update: (id: number, data: Partial<Employee>) => api.put<Employee>(`/employees/${id}/`, data),
  delete: (id: number) => api.delete(`/employees/${id}/`),
};

export const payrollService = {
  getTaxYears: () => api.get<TaxYear[]>('/tax-years/'),
  getRuns: (orgId?: number) => api.get<PayrollRun[]>('/payroll-runs/', { params: { organization_id: orgId } }),
  createRun: (data: Partial<PayrollRun>) => api.post<PayrollRun>('/payroll-runs/', data),
  getRunById: (id: number) => api.get<PayrollRun>(`/payroll-runs/${id}/`),
  finalizeRun: (id: number) => api.patch<PayrollRun>(`/payroll-runs/${id}/`, { status: 'finalized' }),
};

export const payslipService = {
  getByRun: (runId: number) => api.get<Payslip[]>('/payslips/', { params: { payroll_run_id: runId } }),
  getById: (id: number) => api.get<Payslip>(`/payslips/${id}/`),
  downloadPdf: (id: number) => api.get(`/payslips/${id}/download_pdf/`, { responseType: 'blob' }),
};

export default api;
