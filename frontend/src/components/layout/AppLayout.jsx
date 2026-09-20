import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { getHealthStatus } from '../../services/api';

export function AppLayout() {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    let isMounted = true;
    getHealthStatus().then((data) => {
      if (isMounted) {
        setHealthStatus(data);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="h-screen w-screen overflow-hidden flex bg-[#050315] text-[#fbfbfe]">
      {/* Sidebar (Desktop fixed ~230px, mobile drawer) */}
      <Sidebar
        isMobileOpen={isMobileOpen}
        onCloseMobile={() => setIsMobileOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        {/* Top Header */}
        <Header
          onToggleMobileMenu={() => setIsMobileOpen((prev) => !prev)}
          healthStatus={healthStatus}
        />

        {/* Scrollable Page Body */}
        <main className="flex-1 overflow-y-auto bg-[#050315]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
