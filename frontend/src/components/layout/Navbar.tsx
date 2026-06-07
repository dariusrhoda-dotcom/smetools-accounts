import React from 'react';
import { Bell, User, Building2 } from 'lucide-react';
import { useOrganization } from '../../context/OrganizationContext';

const Navbar: React.FC = () => {
  const { organizations, currentOrganization, setCurrentOrganizationId } = useOrganization();

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-8">
      <div className="flex items-center space-x-4">
        <h2 className="text-xl font-semibold text-gray-800">SMETools Payroll</h2>
        
        <div className="flex items-center bg-gray-100 rounded-lg px-3 py-1.5 ml-8 border border-gray-200">
          <Building2 size={18} className="text-gray-500 mr-2" />
          <select 
            value={currentOrganization?.id || ''} 
            onChange={(e) => setCurrentOrganizationId(Number(e.target.value))}
            className="bg-transparent text-sm font-medium text-gray-700 focus:outline-none cursor-pointer"
          >
            {organizations.map(org => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="flex items-center space-x-6">
        <button className="text-gray-500 hover:text-gray-700 relative">
          <Bell size={20} />
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center">3</span>
        </button>
        <div className="flex items-center space-x-3 border-l pl-6 border-gray-200">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">Admin User</p>
            <p className="text-xs text-gray-500">{currentOrganization?.name || 'Loading...'}</p>
          </div>
          <div className="bg-blue-100 p-2 rounded-full text-blue-600">
            <User size={20} />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
