import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const [showReportModal, setShowReportModal] = useState(false);
  const navigate = useNavigate();
  
  const currentDate = new Date();
  const currentMonth = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const currentDateTime = currentDate.toLocaleString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  const stats = [
    { name: `Monthly Appointments (${currentMonth})`, value: '47', change: '+12%', trend: 'up' },
    { name: 'Today\'s Appointments', value: '8', change: '+2', trend: 'up' },
    { name: 'Cancelled This Month', value: '3', change: '-1', trend: 'down' },
    { name: 'Revenue (This Month)', value: '$12,450', change: '+18%', trend: 'up' },
  ];

  const recentAppointments = [
    { id: 1, patient: 'John Doe', treatment: 'Dental Cleaning', time: '09:00 AM', status: 'confirmed' },
    { id: 2, patient: 'Jane Smith', treatment: 'Wisdom Tooth Removal', time: '10:30 AM', status: 'confirmed' },
    { id: 3, patient: 'Bob Johnson', treatment: 'Root Canal', time: '02:00 PM', status: 'confirmed' },
    { id: 4, patient: 'Alice Brown', treatment: 'Checkup', time: '03:30 PM', status: 'completed' },
    { id: 5, patient: 'Charlie Wilson', treatment: 'Filling', time: '04:00 PM', status: 'cancelled' },
  ];

  const generateReport = () => {
    setShowReportModal(true);
  };

  const downloadReport = (reportType: string) => {
    // Generate comprehensive dental practice report
    const reportData = {
      monthly: {
        title: 'Monthly Practice Report',
        period: currentMonth,
        data: [
          'PRACTICE PERFORMANCE SUMMARY',
          `Report Period: ${currentMonth}`,
          `Generated: ${currentDateTime}`,
          '',
          'APPOINTMENT METRICS:',
          '• Total Appointments: 47 (+12% vs last month)',
          '• Confirmed Appointments: 44',
          '• Cancelled Appointments: 3',
          '• Completion Rate: 93.6%',
          '• Average Daily Appointments: 2.3',
          '',
          'REVENUE ANALYSIS:',
          '• Total Revenue: $12,450 (+18% vs last month)',
          '• Average Revenue per Appointment: $282',
          '• Top Revenue Treatments:',
          '  - Root Canal: $4,200 (12 procedures)',
          '  - Crowns: $3,600 (6 procedures)', 
          '  - Cleanings: $2,400 (24 procedures)',
          '',
          'TREATMENT BREAKDOWN:',
          '• Cleanings: 24 appointments (51%)',
          '• Fillings: 8 appointments (17%)',
          '• Root Canals: 6 appointments (13%)',
          '• Extractions: 4 appointments (9%)',
          '• Checkups: 5 appointments (10%)',
          '',
          'PATIENT ANALYTICS:',
          '• New Patients: 12',
          '• Returning Patients: 35',
          '• Patient Retention Rate: 74%',
          '• Average Appointment Duration: 52 minutes',
          '',
          'OPERATIONAL INSIGHTS:',
          '• Peak Hours: 10:00 AM - 2:00 PM',
          '• Busiest Days: Tuesday, Wednesday',
          '• Cancellation Rate: 6.4%',
          '• No-Show Rate: 2.1%',
          '',
          'RECOMMENDATIONS:',
          '• Consider expanding Tuesday/Wednesday hours',
          '• Follow up with cancelled appointments',
          '• Promote preventive care packages',
          '• Schedule equipment maintenance for low-activity periods'
        ]
      },
      yearly: {
        title: 'Annual Practice Report',
        period: currentDate.getFullYear().toString(),
        data: [
          'ANNUAL PRACTICE REPORT',
          `Report Period: ${currentDate.getFullYear()}`,
          `Generated: ${currentDateTime}`,
          '',
          'YEARLY OVERVIEW:',
          '• Total Appointments: 564 (+8% vs last year)',
          '• Total Revenue: $149,400 (+15% vs last year)',
          '• Patient Base: 287 patients',
          '• New Patients Acquired: 144',
          '',
          'MONTHLY TRENDS:',
          'Q1: 138 appointments, $36,200 revenue',
          'Q2: 142 appointments, $37,800 revenue',
          'Q3: 134 appointments, $35,600 revenue',
          'Q4: 150 appointments, $39,800 revenue',
          '',
          'TOP PERFORMING TREATMENTS:',
          '1. Dental Cleanings: 288 procedures, $28,800',
          '2. Root Canals: 72 procedures, $50,400',
          '3. Crowns: 48 procedures, $43,200',
          '4. Fillings: 96 procedures, $14,400',
          '5. Extractions: 60 procedures, $12,600',
          '',
          'PRACTICE EFFICIENCY:',
          '• Average Revenue per Appointment: $265',
          '• Appointment Completion Rate: 94.2%',
          '• Patient Satisfaction Score: 4.8/5',
          '• Equipment Utilization: 87%',
          '',
          'GROWTH OPPORTUNITIES:',
          '• Cosmetic procedures showing 25% growth',
          '• Preventive care could increase by 15%',
          '• Weekend appointments in high demand',
          '• Insurance partnerships expanding coverage'
        ]
      },
      financial: {
        title: 'Financial Summary Report',
        period: currentMonth,
        data: [
          'FINANCIAL PERFORMANCE REPORT',
          `Report Period: ${currentMonth}`,
          `Generated: ${currentDateTime}`,
          '',
          'REVENUE BREAKDOWN:',
          '• Gross Revenue: $12,450',
          '• Insurance Payments: $8,715 (70%)',
          '• Patient Payments: $2,735 (22%)', 
          '• Pending Insurance: $1,000 (8%)',
          '',
          'TREATMENT REVENUE:',
          '• Preventive Care: $3,600 (29%)',
          '• Restorative: $5,400 (43%)',
          '• Surgical: $2,250 (18%)',
          '• Cosmetic: $1,200 (10%)',
          '',
          'PAYMENT ANALYSIS:',
          '• Average Payment Time: 18 days',
          '• Outstanding Receivables: $2,340',
          '• Collection Rate: 96.5%',
          '• Payment Plan Patients: 8',
          '',
          'MONTHLY COMPARISON:',
          '• This Month: $12,450',
          '• Last Month: $10,550 (+18%)',
          '• Same Month Last Year: $11,200 (+11%)',
          '• Year-to-Date: $149,400',
          '',
          'COST ANALYSIS:',
          '• Materials & Supplies: $2,100',
          '• Lab Fees: $890',
          '• Equipment Maintenance: $340',
          '• Net Profit Margin: 72%'
        ]
      }
    };

    const report = reportData[reportType as keyof typeof reportData];
    const csvContent = report.data.join('\n');
    const blob = new Blob([csvContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report.title.replace(/\s+/g, '_')}_${report.period.replace(/\s+/g, '_')}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    setShowReportModal(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between mb-6">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            Dashboard
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Overview of your dental practice
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <button
            type="button"
            onClick={generateReport}
            className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700"
          >
            📊 Generate Report
          </button>
        </div>
      </div>

      {/* Date & Time Card */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow-sm border border-blue-100 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
              <span className="text-white text-2xl">📅</span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                {currentDate.toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  month: 'long', 
                  day: 'numeric', 
                  year: 'numeric' 
                })}
              </h3>
              <p className="text-lg text-blue-600 font-semibold">
                {currentDate.toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit',
                  second: '2-digit'
                })}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-gray-600">Current Status</p>
            <div className="flex items-center mt-1">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
              <span className="text-sm text-green-600 font-semibold">Practice Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                    <span className="text-primary-600 font-bold">📈</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">
                        {stat.value}
                      </div>
                      <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                        stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {stat.trend === 'up' ? '↗' : '↘'}
                        {stat.change}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Appointments */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Appointments</h3>
          </div>
          <div className="p-6">
            <div className="flow-root">
              <ul className="-my-5 divide-y divide-gray-200">
                {recentAppointments.map((appointment) => (
                  <li key={appointment.id} className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-gray-600">
                            {appointment.patient.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {appointment.patient}
                        </p>
                        <p className="text-sm text-gray-500 truncate">
                          {appointment.treatment}
                        </p>
                      </div>
                      <div className="flex-shrink-0 text-sm text-gray-500">
                        {appointment.time}
                      </div>
                      <div className="flex-shrink-0">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(appointment.status)}`}>
                          {appointment.status}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            <div className="mt-6">
              <button 
                onClick={() => navigate('/admin/sheets')}
                className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200"
              >
                View all appointments
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 gap-4">
              <button 
                onClick={() => navigate('/admin/calendar')}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-3">📅</span>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">View Calendar</p>
                    <p className="text-xs text-gray-500">See all appointments</p>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <button 
                onClick={() => navigate('/admin/sheets')}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-3">📋</span>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">Export Data</p>
                    <p className="text-xs text-gray-500">Download booking logs</p>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <button 
                onClick={() => navigate('/admin/chatbot-test')}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-3">🤖</span>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">Test Chatbot</p>
                    <p className="text-xs text-gray-500">Try AI assistant</p>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <button 
                onClick={() => navigate('/admin/qa-editor')}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-3">✏️</span>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">Edit QA</p>
                    <p className="text-xs text-gray-500">Manage chatbot knowledge</p>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <button 
                onClick={() => navigate('/admin/email-management')}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-3">📧</span>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">Email Management</p>
                    <p className="text-xs text-gray-500">Test & preview AI emails</p>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>

              <button 
                onClick={() => navigate('/admin/clinic-settings')}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-3">🏥</span>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">Clinic Settings</p>
                    <p className="text-xs text-gray-500">Manage clinic info & Google reviews</p>
                  </div>
                </div>
                <span className="text-gray-400">→</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">System Status</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
              <span className="text-sm text-gray-700">Internal Calendar: Active</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
              <span className="text-sm text-gray-700">Booking System: Online</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
              <span className="text-sm text-gray-700">AI Chatbot: Connected</span>
            </div>
          </div>
        </div>
      </div>

      {/* Report Generation Modal */}
      {showReportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-white rounded-xl max-w-md w-full shadow-2xl border border-gray-200 overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Generate Practice Report</h3>
                  <p className="text-sm text-gray-600">Select the type of report to generate</p>
                </div>
                <button
                  onClick={() => setShowReportModal(false)}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded-full transition-colors duration-200"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="px-6 py-4 space-y-3">
              <button
                onClick={() => downloadReport('monthly')}
                className="w-full p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-blue-600 text-lg">📅</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Monthly Report</p>
                    <p className="text-sm text-gray-500">Appointments, revenue, and insights for {currentMonth}</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => downloadReport('yearly')}
                className="w-full p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <span className="text-green-600 text-lg">📈</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Annual Report</p>
                    <p className="text-sm text-gray-500">Yearly trends, growth metrics, and performance analysis</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => downloadReport('financial')}
                className="w-full p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <span className="text-purple-600 text-lg">💰</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Financial Summary</p>
                    <p className="text-sm text-gray-500">Revenue breakdown, payments, and financial metrics</p>
                  </div>
                </div>
              </button>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
              <button
                onClick={() => setShowReportModal(false)}
                className="w-full py-2 text-gray-600 text-sm font-medium hover:text-gray-800 transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;