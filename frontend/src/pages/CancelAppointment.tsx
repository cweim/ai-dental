import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface Appointment {
  id: number;
  patient_name: string;
  patient_email: string;
  patient_phone: string;
  appointment_date: string;
  appointment_time: string;
  treatment_type: string;
  notes?: string;
  status: string;
  created_at: string;
}

const CancelAppointment: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<'search' | 'select' | 'reason' | 'success'>('search');
  const [searchData, setSearchData] = useState({
    email: '',
    name: ''
  });
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [cancellationReason, setCancellationReason] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Common cancellation reasons
  const commonReasons = [
    "Schedule conflict",
    "Feeling unwell",
    "Emergency came up", 
    "No longer need treatment",
    "Financial reasons",
    "Need to reschedule",
    "Other"
  ];

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        email: searchData.email,
        ...(searchData.name && { name: searchData.name })
      });

      const response = await fetch(`${API_BASE_URL}/appointments/find?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to find appointments');
      }

      const data = await response.json();
      setAppointments(data);

      if (data.length === 0) {
        setError('No upcoming appointments found for this email and name combination.');
      } else {
        setStep('select');
      }
    } catch (err) {
      setError('Unable to search for appointments. Please check your information and try again.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectAppointment = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setStep('reason');
  };

  const handleCancel = async () => {
    if (!selectedAppointment || !cancellationReason.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/appointments/${selectedAppointment.id}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cancellation_reason: cancellationReason.trim()
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to cancel appointment');
      }

      setStep('success');
    } catch (err: any) {
      setError(err.message || 'Unable to cancel appointment. Please try again or contact us directly.');
      console.error('Cancel error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        weekday: 'long',
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    } catch {
      return dateStr;
    }
  };

  const formatTime = (timeStr: string) => {
    try {
      const [hours, minutes] = timeStr.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${minutes} ${ampm}`;
    } catch {
      return timeStr;
    }
  };

  const getTreatmentName = (type: string) => {
    const treatments: Record<string, string> = {
      'cleaning': 'Dental Cleaning',
      'filling': 'Dental Filling',
      'extraction': 'Tooth Extraction',
      'root_canal': 'Root Canal',
      'crown': 'Dental Crown',
      'whitening': 'Teeth Whitening',
      'consultation': 'Consultation',
      'emergency': 'Emergency Visit'
    };
    return treatments[type] || type;
  };

  const resetForm = () => {
    setStep('search');
    setSearchData({ email: '', name: '' });
    setAppointments([]);
    setSelectedAppointment(null);
    setCancellationReason('');
    setError(null);
  };

  return (
    <div className="min-h-screen" style={{background: 'linear-gradient(to bottom right, #f9fbff, #a3c9f9)'}}>
      {/* Navigation Header */}
      <nav className="relative z-20 px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-gray-900 font-semibold text-xl">SmileCare</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <button
              onClick={() => navigate('/')}
              className="text-blue-600 font-medium text-sm"
            >
              • Home
            </button>
            <a href="#" className="text-gray-700 hover:text-gray-900 text-sm transition-colors">Doctors</a>
            <a href="#" className="text-gray-700 hover:text-gray-900 text-sm transition-colors">Price list</a>
            <a href="#" className="text-gray-700 hover:text-gray-900 text-sm transition-colors">Contact</a>
            <a href="#" className="text-gray-700 hover:text-gray-900 text-sm transition-colors">Team</a>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="text-gray-700 hover:text-gray-900 text-sm transition-colors md:hidden"
            >
              ← Back
            </button>
            <div className="hidden md:block">
              <span className="text-gray-700 text-sm">Eng</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Error Alert */}
          {error && (
            <div className="mb-6 bg-red-50/80 backdrop-blur-sm border-l-4 border-red-400 rounded-xl p-4 shadow-sm border border-red-200">
              <div className="flex items-center">
                <div className="text-red-400">⚠️</div>
                <div className="ml-2 flex-1">
                  <p className="text-sm text-red-800 font-medium">{error}</p>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="ml-auto text-red-400 hover:text-red-600"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {/* Step 1: Search for Appointments */}
          {step === 'search' && (
            <div className="bg-blue-50/80 backdrop-blur-sm rounded-2xl p-6 border border-blue-200 shadow-lg">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-medium text-gray-900 mb-2">Find Your Appointment</h2>
                <p className="text-gray-700">Enter your email and name to find appointments</p>
              </div>

            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  id="email"
                  required
                  value={searchData.email}
                  onChange={(e) => setSearchData({ ...searchData, email: e.target.value })}
                  className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border border-blue-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base shadow-sm"
                  placeholder="Enter the email used for booking"
                />
              </div>

              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name (Optional)
                </label>
                <input
                  type="text"
                  id="name"
                  value={searchData.name}
                  onChange={(e) => setSearchData({ ...searchData, name: e.target.value })}
                  className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border border-blue-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base shadow-sm"
                  placeholder="Enter your full name"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || !searchData.email}
                className="w-full bg-blue-600 text-white py-4 px-6 rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg text-base"
              >
                {isLoading ? '🔍 Searching...' : '🔍 Find Appointments'}
              </button>
            </form>
            </div>
          )}

          {/* Step 2: Select Appointment */}
          {step === 'select' && (
            <div className="bg-blue-50/80 backdrop-blur-sm rounded-2xl p-6 border border-blue-200 shadow-lg">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-medium text-gray-900 mb-2">Select Appointment</h2>
                <p className="text-gray-700">Found {appointments.length} upcoming appointment{appointments.length !== 1 ? 's' : ''}</p>
              </div>

              <div className="space-y-3">
                {appointments.map((appointment) => (
                  <div
                    key={appointment.id}
                    className="bg-white/60 backdrop-blur-sm border border-blue-200 rounded-xl p-4 hover:shadow-md transition-all duration-200 cursor-pointer hover:border-blue-300 hover:bg-white/80"
                    onClick={() => handleSelectAppointment(appointment)}
                  >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="text-xl">🦷</span>
                        <div>
                          <h3 className="font-semibold text-base text-gray-900">
                            {getTreatmentName(appointment.treatment_type)}
                          </h3>
                          <p className="text-xs text-gray-600">with Dr. Smith</p>
                        </div>
                      </div>
                      
                      <div className="space-y-1 text-xs">
                        <div className="flex items-center space-x-2">
                          <span className="text-blue-600">📅</span>
                          <span className="font-medium">{formatDate(appointment.appointment_date)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-blue-600">🕒</span>
                          <span className="font-medium">{formatTime(appointment.appointment_time)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-blue-600">👤</span>
                          <span>{appointment.patient_name}</span>
                        </div>
                      </div>

                      {appointment.notes && (
                        <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                          <p className="text-gray-700">
                            <span className="font-medium">Notes:</span> {appointment.notes}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    <div className="ml-3">
                      <button className="bg-blue-600 text-white px-3 py-2 rounded-xl hover:bg-blue-700 transition-colors duration-200 font-medium text-sm">
                        Cancel
                      </button>
                    </div>
                  </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 text-center">
                <button
                  onClick={resetForm}
                  className="text-gray-600 hover:text-gray-800 font-medium text-sm"
                >
                  ← Search Again
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Cancellation Reason */}
          {step === 'reason' && selectedAppointment && (
            <div className="bg-blue-50/80 backdrop-blur-sm rounded-2xl p-6 border border-blue-200 shadow-lg">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-medium text-gray-900 mb-2">Cancellation Reason</h2>
                <p className="text-gray-700">Please let us know why you're cancelling</p>
              </div>

              {/* Selected Appointment Summary */}
              <div className="bg-blue-100/60 backdrop-blur-sm border border-blue-300 rounded-xl p-4 mb-6">
              <h3 className="font-semibold text-base text-gray-900 mb-2">Appointment to Cancel:</h3>
              <div className="space-y-1 text-xs">
                <div><span className="font-medium">Treatment:</span> {getTreatmentName(selectedAppointment.treatment_type)}</div>
                <div><span className="font-medium">Date:</span> {formatDate(selectedAppointment.appointment_date)}</div>
                <div><span className="font-medium">Time:</span> {formatTime(selectedAppointment.appointment_time)}</div>
                <div><span className="font-medium">Patient:</span> {selectedAppointment.patient_name}</div>
              </div>
            </div>

            {/* Quick Reason Buttons */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select a reason:
              </label>
              <div className="grid grid-cols-2 gap-2">
                {commonReasons.map((reason) => (
                  <button
                    key={reason}
                    onClick={() => setCancellationReason(reason)}
                    className={`p-2 text-xs rounded-xl border transition-all duration-200 ${
                      cancellationReason === reason
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white/80 backdrop-blur-sm text-gray-700 border-blue-200 hover:border-blue-300 hover:bg-blue-50/80'
                    }`}
                  >
                    {reason}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Reason Textarea */}
            <div className="mb-6">
              <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
                Additional Details (Optional)
              </label>
              <textarea
                id="reason"
                rows={3}
                value={cancellationReason}
                onChange={(e) => setCancellationReason(e.target.value)}
                className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border border-blue-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base shadow-sm"
                placeholder="Any additional details..."
              />
            </div>

              <div className="space-y-2">
                <button
                  onClick={handleCancel}
                  disabled={isLoading || !cancellationReason.trim()}
                  className="w-full bg-blue-600 text-white py-4 px-6 rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg text-base"
                >
                  {isLoading ? '⏳ Cancelling...' : '✅ Confirm Cancellation'}
                </button>
                <button
                  onClick={() => setStep('select')}
                  className="w-full bg-white/60 backdrop-blur-sm text-gray-700 py-3 px-6 rounded-xl font-medium hover:bg-white/80 border border-blue-200 transition-all duration-200 text-base"
                >
                  ← Back to Selection
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Success */}
          {step === 'success' && selectedAppointment && (
            <div className="bg-green-50/80 backdrop-blur-sm rounded-2xl shadow-lg border border-green-200 p-6 text-center">
              <div className="w-12 h-12 bg-green-100/80 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-4 border border-green-300">
                <span className="text-2xl">✅</span>
              </div>
              
              <h2 className="text-2xl font-medium text-gray-900 mb-3">Appointment Cancelled</h2>
            
              <div className="bg-green-100/60 backdrop-blur-sm border border-green-300 rounded-xl p-4 mb-6">
              <p className="text-sm text-gray-700 mb-3">
                Your appointment for <strong>{getTreatmentName(selectedAppointment.treatment_type)}</strong> on{' '}
                <strong>{formatDate(selectedAppointment.appointment_date)}</strong> at{' '}
                <strong>{formatTime(selectedAppointment.appointment_time)}</strong> has been cancelled.
              </p>
              
              {cancellationReason && (
                <p className="text-xs text-gray-600">
                  <strong>Reason:</strong> {cancellationReason}
                </p>
              )}
            </div>

              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  We've cancelled any scheduled reminder emails. You can book a new appointment anytime.
                </p>
                
                <div className="space-y-2">
                  <a
                    href="/appointments"
                    className="w-full bg-blue-600 text-white px-4 py-3 rounded-xl font-medium hover:bg-blue-700 transition-all duration-200 shadow-md hover:shadow-lg text-sm inline-block text-center"
                  >
                    📅 Book New Appointment
                  </a>
                  <button
                    onClick={resetForm}
                    className="w-full bg-white/60 backdrop-blur-sm text-gray-700 px-4 py-3 rounded-xl font-medium hover:bg-white/80 border border-blue-200 transition-all duration-200 text-sm"
                  >
                    Cancel Another
                  </button>
                  <button
                    onClick={() => navigate('/')}
                    className="w-full bg-white/40 backdrop-blur-sm text-gray-600 px-4 py-2 rounded-xl font-medium hover:bg-white/60 border border-blue-200 transition-all duration-200 text-sm"
                  >
                    Back to Home
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Contact Information */}
          <div className="mt-8 text-center">
            <div className="bg-blue-50/60 backdrop-blur-sm rounded-2xl p-6 border border-blue-200 inline-block">
              <div className="text-gray-900 space-y-2">
                <div className="font-medium text-lg">(555) 123-4567</div>
                <div className="text-gray-700 text-sm">info@smilecare.com</div>
                <div className="text-gray-500 text-xs mt-4">© 2024 SmileCare Dental Clinic</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CancelAppointment;