import React, { useState, useEffect } from 'react';

interface EmailPreview {
  appointment_id: number;
  email_type: string;
  patient_name: string;
  patient_email: string;
  treatment: string;
  appointment_date: string;
  appointment_time: string;
  subject: string;
  html_content: string;
  plain_text_content: string;
  context_used: {
    patient_notes: string;
    admin_notes: string;
    status: string;
  };
}

interface EmailStats {
  period_days: number;
  reminder_emails: {
    sent: number;
    failed: number;
    success_rate: number;
  };
  followup_emails: {
    sent: number;
    failed: number;
    success_rate: number;
  };
  total: {
    sent: number;
    failed: number;
    success_rate: number;
  };
}

interface Appointment {
  id: string;
  patientName: string;
  email: string;
  date: string;
  time: string;
  treatment: string;
  status: string;
  notes: string;
  adminNotes?: string;
}

const EmailManagement: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [emailPreview, setEmailPreview] = useState<EmailPreview | null>(null);
  const [emailStats, setEmailStats] = useState<EmailStats | null>(null);
  const [selectedAppointment, setSelectedAppointment] = useState<string>('');
  const [emailType, setEmailType] = useState<'reminder' | 'followup'>('reminder');
  const [isLoading, setIsLoading] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Fetch appointments for email testing
  useEffect(() => {
    fetchAppointments();
    fetchEmailStats();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/sheets/bookings?limit=20`);
      if (response.ok) {
        const data = await response.json();
        setAppointments(data.bookings);
      }
    } catch (error) {
      console.error('Error fetching appointments:', error);
    }
  };

  const fetchEmailStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/email/stats?days=30`);
      if (response.ok) {
        const stats = await response.json();
        setEmailStats(stats);
      }
    } catch (error) {
      console.error('Error fetching email stats:', error);
    }
  };

  const previewEmail = async () => {
    if (!selectedAppointment) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/email/preview?appointment_id=${selectedAppointment}&email_type=${emailType}`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        const preview = await response.json();
        setEmailPreview(preview);
        setShowPreview(true);
      } else {
        alert('Failed to generate email preview');
      }
    } catch (error) {
      console.error('Error previewing email:', error);
      alert('Error generating email preview');
    } finally {
      setIsLoading(false);
    }
  };

  const sendTestEmail = async () => {
    if (!testEmail || !selectedAppointment) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/email/send-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to_email: testEmail,
          to_name: 'Test User',
          email_type: emailType,
          appointment_id: parseInt(selectedAppointment)
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Test email sent successfully! Subject: ${result.subject}`);
      } else {
        alert('Failed to send test email');
      }
    } catch (error) {
      console.error('Error sending test email:', error);
      alert('Error sending test email');
    } finally {
      setIsLoading(false);
    }
  };

  const sendManualEmail = async (appointmentId: string, type: 'reminder' | 'followup') => {
    setIsLoading(true);
    try {
      const endpoint = type === 'reminder' ? 'send-reminder' : 'send-followup';
      const response = await fetch(
        `${API_BASE_URL}/api/email/appointments/${appointmentId}/${endpoint}`,
        { method: 'POST' }
      );

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        fetchEmailStats(); // Refresh stats
      } else {
        alert(`Failed to send ${type} email`);
      }
    } catch (error) {
      console.error(`Error sending ${type} email:`, error);
      alert(`Error sending ${type} email`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            📧 Email Management
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Preview, test, and manage automated emails using GROQ AI
          </p>
        </div>
      </div>

      {/* Email Statistics */}
      {emailStats && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Email Statistics (Last 30 Days)</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-800">Reminder Emails</h4>
              <p className="text-2xl font-bold text-blue-600">{emailStats.reminder_emails.sent}</p>
              <p className="text-sm text-blue-600">
                Success Rate: {emailStats.reminder_emails.success_rate.toFixed(1)}%
              </p>
              {emailStats.reminder_emails.failed > 0 && (
                <p className="text-sm text-red-600">{emailStats.reminder_emails.failed} failed</p>
              )}
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-800">Follow-up Emails</h4>
              <p className="text-2xl font-bold text-green-600">{emailStats.followup_emails.sent}</p>
              <p className="text-sm text-green-600">
                Success Rate: {emailStats.followup_emails.success_rate.toFixed(1)}%
              </p>
              {emailStats.followup_emails.failed > 0 && (
                <p className="text-sm text-red-600">{emailStats.followup_emails.failed} failed</p>
              )}
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-semibold text-purple-800">Total Emails</h4>
              <p className="text-2xl font-bold text-purple-600">{emailStats.total.sent}</p>
              <p className="text-sm text-purple-600">
                Success Rate: {emailStats.total.success_rate.toFixed(1)}%
              </p>
              {emailStats.total.failed > 0 && (
                <p className="text-sm text-red-600">{emailStats.total.failed} failed</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Email Testing */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🧪 Email Testing & Preview</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Email Configuration */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Appointment
              </label>
              <select
                value={selectedAppointment}
                onChange={(e) => setSelectedAppointment(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Choose an appointment...</option>
                {appointments.map((appointment) => (
                  <option key={appointment.id} value={appointment.id}>
                    {appointment.patientName} - {appointment.treatment} ({appointment.date})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Type
              </label>
              <select
                value={emailType}
                onChange={(e) => setEmailType(e.target.value as 'reminder' | 'followup')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="reminder">Reminder Email (24h before)</option>
                <option value="followup">Follow-up Email (2h after)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Test Email Address
              </label>
              <input
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="your-email@example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={previewEmail}
                disabled={!selectedAppointment || isLoading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Generating...' : '👁️ Preview Email'}
              </button>
              
              <button
                onClick={sendTestEmail}
                disabled={!selectedAppointment || !testEmail || isLoading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Sending...' : '📤 Send Test'}
              </button>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-4">
            <h4 className="font-semibold text-gray-900">Quick Actions</h4>
            
            {selectedAppointment && (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  Selected: {appointments.find(a => a.id === selectedAppointment)?.patientName}
                </p>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => sendManualEmail(selectedAppointment, 'reminder')}
                    disabled={isLoading}
                    className="px-3 py-2 bg-yellow-600 text-white text-sm rounded-md hover:bg-yellow-700 disabled:bg-gray-400"
                  >
                    Send Reminder Now
                  </button>
                  
                  <button
                    onClick={() => sendManualEmail(selectedAppointment, 'followup')}
                    disabled={isLoading}
                    className="px-3 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700 disabled:bg-gray-400"
                  >
                    Send Follow-up Now
                  </button>
                </div>
              </div>
            )}

            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h5 className="font-medium text-gray-900 mb-2">💡 How it works:</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Select an appointment to use real patient data</li>
                <li>• GROQ AI generates personalized content</li>
                <li>• Includes patient notes and admin notes</li>
                <li>• Preview before sending to patients</li>
                <li>• Test with your own email first</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Email Preview Modal */}
      {showPreview && emailPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-screen overflow-y-auto shadow-2xl">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-gray-900">📧 Email Preview</h3>
                <p className="text-sm text-gray-600">
                  {emailPreview.email_type.charAt(0).toUpperCase() + emailPreview.email_type.slice(1)} email for {emailPreview.patient_name}
                </p>
              </div>
              <button
                onClick={() => setShowPreview(false)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-full"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Body */}
            <div className="px-6 py-4 space-y-4">
              {/* Email Details */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-700">To:</p>
                  <p className="text-sm text-gray-900">{emailPreview.patient_email}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Subject:</p>
                  <p className="text-sm text-gray-900">{emailPreview.subject}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Treatment:</p>
                  <p className="text-sm text-gray-900">{emailPreview.treatment}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Appointment:</p>
                  <p className="text-sm text-gray-900">{emailPreview.appointment_date} at {emailPreview.appointment_time}</p>
                </div>
              </div>

              {/* Context Used */}
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">🤖 AI Context Used:</h4>
                <div className="text-sm text-blue-800 space-y-1">
                  {emailPreview.context_used.patient_notes && (
                    <p><strong>Patient Notes:</strong> {emailPreview.context_used.patient_notes}</p>
                  )}
                  {emailPreview.context_used.admin_notes && (
                    <p><strong>Admin Notes:</strong> {emailPreview.context_used.admin_notes}</p>
                  )}
                  <p><strong>Status:</strong> {emailPreview.context_used.status}</p>
                </div>
              </div>

              {/* Email Content */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-100 px-4 py-2 border-b border-gray-200">
                  <h4 className="font-medium text-gray-900">Email Content (HTML)</h4>
                </div>
                <div 
                  className="p-4 max-h-96 overflow-y-auto"
                  dangerouslySetInnerHTML={{ __html: emailPreview.html_content }}
                />
              </div>

              {/* Plain Text Version */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-100 px-4 py-2 border-b border-gray-200">
                  <h4 className="font-medium text-gray-900">Plain Text Version</h4>
                </div>
                <div className="p-4 max-h-64 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700">
                    {emailPreview.plain_text_content}
                  </pre>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowPreview(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Close
              </button>
              <button
                onClick={sendTestEmail}
                disabled={!testEmail || isLoading}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Sending...' : 'Send Test Email'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailManagement;