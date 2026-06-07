import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2 } from 'lucide-react';
import { Employee } from '../types';
import { employeeService } from '../services/api';
import { useOrganization } from '../context/OrganizationContext';

const Employees: React.FC = () => {
  const { currentOrganization } = useOrganization();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentEmployee, setCurrentEmployee] = useState<Partial<Employee> | null>(null);

  useEffect(() => {
    fetchEmployees();
  }, [currentOrganization]);

  const fetchEmployees = async () => {
    if (!currentOrganization) return;
    
    try {
      setLoading(true);
      const response = await employeeService.getAll(currentOrganization.id);
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentEmployee || !currentOrganization) return;

    try {
      if (currentEmployee.id) {
        await employeeService.update(currentEmployee.id, currentEmployee);
      } else {
        await employeeService.create({ ...currentEmployee, organization: currentOrganization.id });
      }
      setIsModalOpen(false);
      fetchEmployees();
    } catch (error) {
      console.error('Error saving employee:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await employeeService.delete(id);
        fetchEmployees();
      } catch (error) {
        console.error('Error deleting employee:', error);
      }
    }
  };

  const filteredEmployees = employees.filter(emp => 
    `${emp.first_name} ${emp.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.employee_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Employee Management</h1>
        <button 
          onClick={() => { setCurrentEmployee({}); setIsModalOpen(true); }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors"
        >
          <Plus size={18} />
          <span>Add Employee</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <div className="relative w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search employees..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading employees...</div>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 text-gray-500 text-sm">
                <th className="px-6 py-4 font-medium">Employee Name</th>
                <th className="px-6 py-4 font-medium">Code</th>
                <th className="px-6 py-4 font-medium">ID Number</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredEmployees.map((emp) => (
                <tr key={emp.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">
                        {emp.first_name[0]}{emp.last_name[0]}
                      </div>
                      <span className="font-medium">{emp.first_name} {emp.last_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-600 text-sm">{emp.employee_code}</td>
                  <td className="px-6 py-4 text-gray-600 text-sm">{emp.id_number}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      emp.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {emp.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end space-x-2">
                      <button 
                        onClick={() => { setCurrentEmployee(emp); setIsModalOpen(true); }}
                        className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                      >
                        <Edit size={18} />
                      </button>
                      <button 
                        onClick={() => handleDelete(emp.id)}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredEmployees.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">No employees found</td>
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
              <h2 className="text-xl font-bold">{currentEmployee?.id ? 'Edit Employee' : 'Add Employee'}</h2>
            </div>
            <form onSubmit={handleSave} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                  <input 
                    type="text" 
                    required
                    value={currentEmployee?.first_name || ''}
                    onChange={(e) => setCurrentEmployee({...currentEmployee, first_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                  <input 
                    type="text" 
                    required
                    value={currentEmployee?.last_name || ''}
                    onChange={(e) => setCurrentEmployee({...currentEmployee, last_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Employee Code</label>
                <input 
                  type="text" 
                  required
                  value={currentEmployee?.employee_code || ''}
                  onChange={(e) => setCurrentEmployee({...currentEmployee, employee_code: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ID Number</label>
                <input 
                  type="text" 
                  value={currentEmployee?.id_number || ''}
                  onChange={(e) => setCurrentEmployee({...currentEmployee, id_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Join Date</label>
                  <input 
                    type="date" 
                    required
                    value={currentEmployee?.join_date || ''}
                    onChange={(e) => setCurrentEmployee({...currentEmployee, join_date: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                  <input 
                    type="date" 
                    required
                    value={currentEmployee?.date_of_birth || ''}
                    onChange={(e) => setCurrentEmployee({...currentEmployee, date_of_birth: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Medical Dependents</label>
                  <input 
                    type="number" 
                    min="0"
                    value={currentEmployee?.medical_dependents || 0}
                    onChange={(e) => setCurrentEmployee({...currentEmployee, medical_dependents: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ETI Months Claimed</label>
                  <input 
                    type="number" 
                    min="0"
                    max="24"
                    value={currentEmployee?.eti_months_claimed || 0}
                    onChange={(e) => setCurrentEmployee({...currentEmployee, eti_months_claimed: parseInt(e.target.value)})}
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
                  Save Employee
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Employees;
