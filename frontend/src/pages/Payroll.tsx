import React, { useState, useEffect } from 'react';
import { Play, Download, Eye, ArrowLeft, CheckCircle } from 'lucide-react';
import { PayrollRun, Payslip, TaxYear } from '../types';
import { payrollService, payslipService } from '../services/api';
import { useOrganization } from '../context/OrganizationContext';

const Payroll: React.FC = () => {
  const { currentOrganization } = useOrganization();
  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [taxYears, setTaxYears] = useState<TaxYear[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRun, setSelectedRun] = useState<PayrollRun | null>(null);
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [newRun, setNewRun] = useState({
    tax_year: '',
    period_month: new Date().getMonth() + 1,
    period_year: new Date().getFullYear(),
  });

  useEffect(() => {
    fetchInitialData();
  }, [currentOrganization]);

  const fetchInitialData = async () => {
    if (!currentOrganization) return;
    
    try {
      setLoading(true);
      const [runsRes, yearsRes] = await Promise.all([
        payrollService.getRuns(currentOrganization.id),
        payrollService.getTaxYears(),
      ]);
      setRuns(runsRes.data);
      setTaxYears(yearsRes.data);
    } catch (error) {
      console.error('Error fetching payroll data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentOrganization) return;

    try {
      await payrollService.createRun({
        ...newRun,
        organization: currentOrganization.id,
        tax_year: parseInt(newRun.tax_year),
      });
      setIsModalOpen(false);
      fetchInitialData();
    } catch (error) {
      console.error('Error creating payroll run:', error);
    }
  };

  const viewRunDetails = async (run: PayrollRun) => {
    try {
      setSelectedRun(run);
      const response = await payslipService.getByRun(run.id);
      setPayslips(response.data);
    } catch (error) {
      console.error('Error fetching payslips:', error);
    }
  };

  const handleFinalize = async (id: number) => {
    if (window.confirm('Are you sure you want to finalize this payroll run? This will lock the data.')) {
      try {
        await payrollService.finalizeRun(id);
        if (selectedRun && selectedRun.id === id) {
          setSelectedRun({ ...selectedRun, status: 'finalized' });
        }
        fetchInitialData();
      } catch (error) {
        console.error('Error finalizing payroll run:', error);
      }
    }
  };

  const downloadPayslip = async (id: number, employeeName: string) => {
    try {
      const response = await payslipService.downloadPdf(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payslip_${employeeName.replace(' ', '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading payslip:', error);
      alert('PDF generation might not be implemented on the backend yet.');
    }
  };

  if (selectedRun) {
    return (
      <div>
        <button 
          onClick={() => setSelectedRun(null)}
          className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 mb-6 transition-colors"
        >
          <ArrowLeft size={18} />
          <span>Back to Payroll Runs</span>
        </button>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Payroll Run: {selectedRun.period_month}/{selectedRun.period_year}</h1>
            <p className="text-gray-500">Status: <span className="capitalize font-medium">{selectedRun.status}</span></p>
          </div>
          {selectedRun.status === 'draft' && (
            <button 
              onClick={() => handleFinalize(selectedRun.id)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-green-700 transition-colors"
            >
              <CheckCircle size={18} />
              <span>Finalize Run</span>
            </button>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 text-gray-500 text-sm bg-gray-50/50">
                <th className="px-6 py-4 font-medium">Employee</th>
                <th className="px-6 py-4 font-medium">Gross Income</th>
                <th className="px-6 py-4 font-medium">PAYE</th>
                <th className="px-6 py-4 font-medium">Net Pay</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {payslips.map((slip) => (
                <tr key={slip.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-medium">Employee ID: {slip.employee}</td>
                  <td className="px-6 py-4">R {slip.gross_income}</td>
                  <td className="px-6 py-4 text-red-600">R {slip.paye}</td>
                  <td className="px-6 py-4 font-bold text-green-700">R {slip.net_pay}</td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => downloadPayslip(slip.id, `ID_${slip.employee}`)}
                      className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                      title="Download Payslip PDF"
                    >
                      <Download size={18} />
                    </button>
                  </td>
                </tr>
              ))}
              {payslips.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">No payslips generated for this run yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Payroll Runs</h1>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors"
        >
          <Play size={18} />
          <span>New Payroll Run</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading payroll runs...</div>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 text-gray-500 text-sm bg-gray-50/50">
                <th className="px-6 py-4 font-medium">Period</th>
                <th className="px-6 py-4 font-medium">Tax Year</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {runs.map((run) => (
                <tr key={run.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-medium">{run.period_month}/{run.period_year}</td>
                  <td className="px-6 py-4 text-gray-600 text-sm">{run.tax_year}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      run.status === 'finalized' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => viewRunDetails(run)}
                      className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                      title="View Details"
                    >
                      <Eye size={18} />
                    </button>
                  </td>
                </tr>
              ))}
              {runs.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">No payroll runs found</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-xl font-bold">New Payroll Run</h2>
            </div>
            <form onSubmit={handleCreateRun} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tax Year</label>
                <select 
                  required
                  value={newRun.tax_year}
                  onChange={(e) => setNewRun({...newRun, tax_year: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Tax Year</option>
                  {taxYears.map(year => (
                    <option key={year.id} value={year.id}>{year.label}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Month (1-12)</label>
                  <input 
                    type="number" 
                    min="1" max="12"
                    required
                    value={newRun.period_month}
                    onChange={(e) => setNewRun({...newRun, period_month: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                  <input 
                    type="number" 
                    required
                    value={newRun.period_year}
                    onChange={(e) => setNewRun({...newRun, period_year: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button 
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create Run
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Payroll;
