import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import AdminLayout from './components/AdminLayout';
import Landing from './pages/Landing';
import Home from './pages/Home';
import Appointments from './pages/Appointments';
import Chat from './pages/Chat';
import CancelAppointment from './pages/CancelAppointment';
import Dashboard from './pages/admin/Dashboard';
import CalendarView from './pages/admin/CalendarView';
import SheetsView from './pages/admin/SheetsView';
import QAEditor from './pages/admin/QAEditor';
import ChatbotTester from './pages/admin/ChatbotTester';
import EmailManagement from './pages/admin/EmailManagement';
import ClinicSettings from './pages/admin/ClinicSettings';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Landing />} />
          <Route path="chat" element={<Chat />} />
          <Route path="appointments" element={<Appointments />} />
          <Route path="cancel-appointment" element={<CancelAppointment />} />
          <Route path="home" element={<Home />} />
        </Route>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="calendar" element={<CalendarView />} />
          <Route path="sheets" element={<SheetsView />} />
          <Route path="qa-editor" element={<QAEditor />} />
          <Route path="chatbot-test" element={<ChatbotTester />} />
          <Route path="email-management" element={<EmailManagement />} />
          <Route path="clinic-settings" element={<ClinicSettings />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
