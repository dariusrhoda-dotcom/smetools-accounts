import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Organization } from '../types';
import { organizationService } from '../services/api';

interface OrganizationContextType {
  organizations: Organization[];
  currentOrganization: Organization | null;
  setCurrentOrganizationId: (id: number) => void;
  isLoading: boolean;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

export const OrganizationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [currentOrganizationId, setCurrentOrganizationIdState] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchOrgs = async () => {
      try {
        const response = await organizationService.getAll();
        setOrganizations(response.data);
        if (response.data.length > 0 && currentOrganizationId === null) {
          // Default to first organization if none selected
          setCurrentOrganizationIdState(response.data[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch organizations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchOrgs();
  }, []);

  const setCurrentOrganizationId = (id: number) => {
    setCurrentOrganizationIdState(id);
    // Persist to local storage if needed
    localStorage.setItem('currentOrganizationId', id.toString());
  };

  // Load from local storage on init
  useEffect(() => {
    const savedId = localStorage.getItem('currentOrganizationId');
    if (savedId) {
      setCurrentOrganizationIdState(parseInt(savedId, 10));
    }
  }, []);

  const currentOrganization = organizations.find(org => org.id === currentOrganizationId) || null;

  return (
    <OrganizationContext.Provider value={{ 
      organizations, 
      currentOrganization, 
      setCurrentOrganizationId,
      isLoading 
    }}>
      {children}
    </OrganizationContext.Provider>
  );
};

export const useOrganization = () => {
  const context = useContext(OrganizationContext);
  if (context === undefined) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  return context;
};
