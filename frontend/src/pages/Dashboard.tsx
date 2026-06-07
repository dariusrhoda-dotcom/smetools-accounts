import React, { useEffect, useState } from 'react';
import { useOrganization } from '../context/OrganizationContext';
import { organizationService } from '../services/api';

const Dashboard: React.FC = () => {
  const { currentOrganization } = useOrganization();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      if (!currentOrganization) return;
      
      try {
        setLoading(true);
        const response = await organizationService.getStats(currentOrganization.id);
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [currentOrganization]);

  if (loading) {
    return <div className="p-8">Loading dashboard metrics...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Payroll Dashboard - {currentOrganization?.name}</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500 mb-1">Total Employees</p>
          <p className="text-3xl font-bold">{stats?.employee_count || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500 mb-1">Total PAYE (MTD)</p>
          <p className="text-3xl font-bold">R {(stats?.total_paye_mtd || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500 mb-1">Net Payroll (MTD)</p>
          <p className="text-3xl font-bold">R {(stats?.total_net_mtd || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {stats?.recent_runs?.length > 0 ? (
            stats.recent_runs.map((run: any) => (
              <div key={run.id} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 ${run.status === 'finalized' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'} rounded-full flex items-center justify-center`}>
                    PY
                  </div>
                  <div>
                    <p className="font-medium">Payroll Run {run.status.charAt(0).toUpperCase() + run.status.slice(1)}</p>
                    <p className="text-xs text-gray-500">Period: {run.period} • {run.employee_count} employees</p>
                  </div>
                </div>
                <a href={`/payroll`} className="text-blue-600 text-sm font-medium hover:underline cursor-pointer">View Runs</a>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-sm">No recent payroll activity found.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
