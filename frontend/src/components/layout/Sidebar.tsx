import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Calculator, Settings, HelpCircle } from 'lucide-react';

const Sidebar: React.FC = () => {
  const menuItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Employees', path: '/employees', icon: <Users size={20} /> },
    { name: 'Payroll', path: '/payroll', icon: <Calculator size={20} /> },
    { name: 'Tax Expert', path: '/tax-expert', icon: <HelpCircle size={20} /> },
    { name: 'Settings', path: '/settings', icon: <Settings size={20} /> },
  ];

  return (
    <div className="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-blue-500">SMETools Payroll</h1>
      </div>
      <nav className="flex-1 px-4 py-4 space-y-2">
        {menuItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            {item.icon}
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
