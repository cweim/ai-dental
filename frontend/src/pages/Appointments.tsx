import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface TreatmentType {
  name: string;
  duration: number;
  description: string;
  price: number;
}

interface TreatmentTypes {
  [key: string]: TreatmentType;
}

const Appointments: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    date: '',
    time: '',
    treatment: '',
    notes: ''
  });

  const [treatmentTypes, setTreatmentTypes] = useState<TreatmentTypes>({});
  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [appointmentDetails, setAppointmentDetails] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Load treatment types on component mount
  useEffect(() => {
    const fetchTreatmentTypes = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/treatments/types`);
        if (!response.ok) throw new Error('Failed to fetch treatment types');
        const data = await response.json();
        setTreatmentTypes(data);
      } catch (error) {
        console.error('Error fetching treatment types:', error);
        setError('Unable to load treatment types. Please refresh the page.');
      }
    };
    
    fetchTreatmentTypes();
  }, [API_BASE_URL]);

  // Load available slots when date or treatment changes
  useEffect(() => {
    if (formData.date && formData.treatment) {
      fetchAvailableSlots();
    } else {
      setAvailableSlots([]);
    }
  }, [formData.date, formData.treatment]);

  const fetchAvailableSlots = async () => {
    setLoadingSlots(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/appointments/available-slots?date=${formData.date}&treatment=${formData.treatment}`
      );
      if (!response.ok) throw new Error('Failed to fetch available slots');
      const data = await response.json();
      setAvailableSlots(data.available_slots || []);
    } catch (error) {
      console.error('Error fetching available slots:', error);
      setAvailableSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Reset time when date or treatment changes
    if (name === 'date' || name === 'treatment') {
      setFormData(prev => ({
        ...prev,
        time: ''
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/appointments/book`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to book appointment');
      }

      const result = await response.json();
      setAppointmentDetails({
        patient_name: formData.name,
        treatment_name: treatmentTypes[formData.treatment]?.name || formData.treatment,
        date: formData.date,
        time: formData.time,
        duration: treatmentTypes[formData.treatment]?.duration || 60,
        price: treatmentTypes[formData.treatment]?.price || 0
      });
      setShowSuccessModal(true);
    } catch (error: any) {
      setError(error.message || 'Unable to book appointment. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const formatTimeSlot = (timeSlot: string) => {
    try {
      const [hours, minutes] = timeSlot.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${minutes} ${ampm}`;
    } catch {
      return timeSlot;
    }
  };

  const formatDisplayDate = (dateStr: string) => {
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Mobile-First Header */}
      <div className="bg-white shadow-lg border-b border-blue-100 sticky top-0 z-10">
        <div className="px-4 py-3">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate('/')}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
              title="Back to Home"
            >
              ← Back
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-blue-700 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-white text-xl">📅</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">Book Appointment</h1>
                <p className="text-xs text-blue-600 font-medium">Schedule your dental visit</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile-First Container */}
      <div className="px-4 py-6">
        {/* Error Alert */}
        {error && (
          <div className="mb-4 bg-red-50 border-l-4 border-red-400 rounded-lg p-3 shadow-sm">
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

        <div className="bg-white rounded-xl shadow-lg p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                placeholder="Enter your full name"
              />
            </div>
              
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                placeholder="Enter your email address"
              />
            </div>

            {/* Phone */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number *
              </label>
              <input
                type="tel"
                id="phone"
                name="phone"
                required
                value={formData.phone}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                placeholder="(555) 123-4567"
              />
            </div>
              
            {/* Treatment */}
            <div>
              <label htmlFor="treatment" className="block text-sm font-medium text-gray-700 mb-2">
                Treatment Type *
              </label>
              <select
                id="treatment"
                name="treatment"
                required
                value={formData.treatment}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
              >
                <option value="">Select a treatment</option>
                {Object.entries(treatmentTypes).map(([key, treatment]) => (
                  <option key={key} value={key}>
                    {treatment.name} - ${treatment.price} ({treatment.duration} min)
                  </option>
                ))}
              </select>
            </div>

            {/* Date */}
            <div>
              <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Date *
              </label>
              <input
                type="date"
                id="date"
                name="date"
                required
                value={formData.date}
                onChange={handleInputChange}
                min={getTodayDate()}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
              />
            </div>
              
            {/* Time */}
            <div>
              <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Time *
              </label>
              <select
                id="time"
                name="time"
                required
                value={formData.time}
                onChange={handleInputChange}
                disabled={!formData.date || !formData.treatment || loadingSlots}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-base"
              >
                <option value="">
                  {loadingSlots ? 'Loading available times...' : 'Select a time'}
                </option>
                {availableSlots.map((slot) => (
                  <option key={slot} value={slot}>
                    {formatTimeSlot(slot)}
                  </option>
                ))}
              </select>
              {formData.date && formData.treatment && availableSlots.length === 0 && !loadingSlots && (
                <p className="text-sm text-red-600 mt-2">
                  No available slots for this date. Please select a different date.
                </p>
              )}
            </div>

            {/* Notes */}
            <div>
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                Additional Notes (Optional)
              </label>
              <textarea
                id="notes"
                name="notes"
                rows={3}
                value={formData.notes}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                placeholder="Any specific concerns or questions..."
              />
            </div>

            {/* Submit Button */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={isSubmitting || !formData.name || !formData.email || !formData.phone || !formData.date || !formData.time || !formData.treatment}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 px-6 rounded-lg font-medium text-base hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                {isSubmitting ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Booking...
                  </div>
                ) : (
                  '📅 Book Appointment'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Success Modal - Mobile Optimized */}
      {showSuccessModal && appointmentDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl w-full max-w-sm p-6 shadow-2xl">
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">✅</span>
              </div>
              
              <h2 className="text-xl font-bold text-gray-900 mb-3">
                Appointment Booked!
              </h2>
              
              <div className="bg-green-50 rounded-lg p-3 mb-4 text-left">
                <h3 className="font-semibold text-gray-900 mb-2 text-sm">Details:</h3>
                <div className="space-y-1 text-xs text-gray-700">
                  <p><span className="font-medium">Patient:</span> {appointmentDetails.patient_name}</p>
                  <p><span className="font-medium">Treatment:</span> {appointmentDetails.treatment_name}</p>
                  <p><span className="font-medium">Date:</span> {formatDisplayDate(appointmentDetails.date)}</p>
                  <p><span className="font-medium">Time:</span> {formatTimeSlot(appointmentDetails.time)}</p>
                  <p><span className="font-medium">Duration:</span> {appointmentDetails.duration} min</p>
                  <p><span className="font-medium">Price:</span> ${appointmentDetails.price}</p>
                </div>
              </div>
              
              <p className="text-gray-600 mb-4 text-sm">
                Confirmation email sent! You'll get a reminder 24 hours before your appointment.
              </p>
              
              <div className="space-y-2">
                <button
                  onClick={() => {
                    setShowSuccessModal(false);
                    setFormData({
                      name: '',
                      email: '',
                      phone: '',
                      date: '',
                      time: '',
                      treatment: '',
                      notes: ''
                    });
                  }}
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-blue-800 transition-all duration-200 text-sm"
                >
                  Book Another
                </button>
                
                <button
                  onClick={() => navigate('/')}
                  className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-200 transition-all duration-200 text-sm"
                >
                  Back to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments;