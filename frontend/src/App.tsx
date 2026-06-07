import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Employees from './pages/Employees';
import Payroll from './pages/Payroll';
import TaxExpertPage from './pages/TaxExpertPage';
import { OrganizationProvider } from './context/OrganizationContext';

function App() {
  return (
    <OrganizationProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="employees" element={<Employees />} />
            <Route path="payroll" element={<Payroll />} />
            <Route path="tax-expert" element={<TaxExpertPage />} />
            <Route path="settings" element={<div className="p-8"><h1 className="text-2xl font-bold">Settings (Coming Soon)</h1></div>} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </OrganizationProvider>
  );
}

export default App;
