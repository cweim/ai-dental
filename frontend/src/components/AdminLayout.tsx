import React, { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

const AdminLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const navigation = [
    { name: 'Dashboard', href: '/admin', icon: '📊' },
    { name: 'Calendar', href: '/admin/calendar', icon: '📅' },
    { name: 'Booking Logs', href: '/admin/sheets', icon: '📋' },
    { name: 'Email Management', href: '/admin/email-management', icon: '📧' },
    { name: 'Clinic Settings', href: '/admin/clinic-settings', icon: '🏥' },
    { name: 'QA Manager', href: '/admin/qa-editor', icon: '✏️' },
    { name: 'Chatbot Test', href: '/admin/chatbot-test', icon: '🤖' },
  ];

  const isActive = (href: string) => {
    if (href === '/admin') {
      return location.pathname === '/admin';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Mobile menu button */}
      <div className="lg:hidden">
        <div className="flex items-center justify-between bg-white px-4 py-3 border-b border-gray-200">
          <h1 className="text-xl font-semibold text-gray-900">Admin Dashboard</h1>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'block' : 'hidden'} lg:block fixed lg:relative inset-y-0 left-0 z-50 w-64 bg-white shadow-lg`}>
          <div className="flex flex-col h-full">
            {/* Logo */}
            <div className="flex items-center justify-center h-16 px-4 bg-primary-600">
              <h1 className="text-xl font-bold text-white">AI Dentist Admin</h1>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-4 space-y-2">
              {navigation.map((item) => (
                <button
                  key={item.name}
                  onClick={() => {
                    navigate(item.href);
                    setSidebarOpen(false);
                  }}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive(item.href)
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <span className="mr-3 text-lg">{item.icon}</span>
                  {item.name}
                </button>
              ))}
            </nav>

            {/* User info */}
            <div className="px-4 py-4 border-t border-gray-200">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-600">👤</span>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">Admin User</p>
                  <p className="text-xs text-gray-500">admin@aidentiist.com</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <div
            className="lg:hidden fixed inset-0 z-40 bg-black bg-opacity-50"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main content */}
        <div className="flex-1 lg:ml-0">
          <main className="p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export default AdminLayout;