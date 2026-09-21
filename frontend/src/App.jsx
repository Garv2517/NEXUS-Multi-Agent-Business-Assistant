import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { Overview } from './pages/Overview';
import { Assistant } from './pages/Assistant';
import { Sales } from './pages/Sales';
import { Inventory } from './pages/Inventory';
import { HR } from './pages/HR';
import { Activity } from './pages/Activity';
import { About } from './pages/About';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Overview />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="sales" element={<Sales />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="hr" element={<HR />} />
        <Route path="activity" element={<Activity />} />
        <Route path="about" element={<About />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
