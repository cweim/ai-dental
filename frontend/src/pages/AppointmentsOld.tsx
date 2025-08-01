import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

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
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [appointmentDetails, setAppointmentDetails] = useState<any>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Load treatment types on component mount
  useEffect(() => {
    const fetchTreatmentTypes = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/treatments/types`);
        setTreatmentTypes(response.data);
      } catch (error) {
        console.error('Error fetching treatment types:', error);
      }
    };
    
    fetchTreatmentTypes();
  }, [API_BASE_URL]);

  // Fetch available slots when date or treatment changes
  useEffect(() => {
    if (formData.date && formData.treatment) {
      fetchAvailableSlots();
    }
  }, [formData.date, formData.treatment]);

  const fetchAvailableSlots = async () => {
    setLoadingSlots(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/appointments/available-slots`, {
        params: {
          date: formData.date,
          treatment: formData.treatment
        }
      });
      setAvailableSlots(response.data.available_slots);
    } catch (error) {
      console.error('Error fetching available slots:', error);
      setAvailableSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const response = await axios.post(`${API_BASE_URL}/appointments/book`, formData);
      
      if (response.status === 200) {
        setSubmitStatus('success');
        setAppointmentDetails(response.data);
        setShowSuccessModal(true);
        
        // Reset form
        setFormData({
          name: '',
          email: '',
          phone: '',
          date: '',
          time: '',
          treatment: '',
          notes: ''
        });
        setAvailableSlots([]);
      }
    } catch (error) {
      console.error('Error booking appointment:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
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

  const formatTime = (time: string) => {
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 90); // 3 months from now
    return maxDate.toISOString().split('T')[0];
  };

  const handleSuccessModalClose = () => {
    setShowSuccessModal(false);
    navigate('/chat');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Book an Appointment</h1>
      
      {submitStatus === 'success' && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">
                Appointment booked successfully! You'll receive a confirmation email shortly.
              </p>
            </div>
          </div>
        </div>
      )}

      {submitStatus === 'error' && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">
                Error booking appointment. Please try again or contact us directly.
              </p>
            </div>
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Treatment Selection */}
        <div>
          <label htmlFor="treatment" className="block text-sm font-medium text-gray-700 mb-2">
            Treatment Type
          </label>
          <select
            id="treatment"
            name="treatment"
            value={formData.treatment}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="">Select treatment</option>
            {Object.entries(treatmentTypes).map(([key, treatment]) => (
              <option key={key} value={key}>
                {treatment.name} - ${treatment.price} ({treatment.duration} min)
              </option>
            ))}
          </select>
          {formData.treatment && treatmentTypes[formData.treatment] && (
            <p className="mt-2 text-sm text-gray-600">
              {treatmentTypes[formData.treatment].description}
            </p>
          )}
        </div>

        {/* Date Selection */}
        <div>
          <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
            Preferred Date
          </label>
          <input
            type="date"
            id="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            min={getTodayDate()}
            max={getMaxDate()}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
        </div>

        {/* Time Selection */}
        {formData.date && formData.treatment && (
          <div>
            <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-2">
              Available Time Slots
            </label>
            {loadingSlots ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                <span className="ml-2 text-gray-600">Loading available slots...</span>
              </div>
            ) : availableSlots.length > 0 ? (
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                {availableSlots.map((slot) => (
                  <button
                    key={slot}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, time: slot }))}
                    className={`px-3 py-2 text-sm rounded-md border ${
                      formData.time === slot
                        ? 'bg-primary-600 text-white border-primary-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {formatTime(slot)}
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 py-4">
                No available slots for the selected date and treatment. Please choose a different date.
              </p>
            )}
          </div>
        )}

        {/* Contact Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Full Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
              Phone Number
            </label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          
          <div className="md:col-span-2">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
        </div>
        
        {/* Additional Notes */}
        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
            Additional Notes (Optional)
          </label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={3}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Any special requests or information we should know..."
          />
        </div>
        
        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting || !formData.time}
          className={`w-full py-3 px-4 rounded-md transition-colors ${
            isSubmitting || !formData.time
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
          } text-white font-medium`}
        >
          {isSubmitting ? 'Booking Appointment...' : 'Book Appointment'}
        </button>
      </form>

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl max-w-md w-full p-8 shadow-2xl border border-green-200">
            {/* Success Icon */}
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
              <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            
            {/* Success Message */}
            <div className="text-center">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                🎉 Appointment Booked Successfully!
              </h3>
              <p className="text-gray-600 mb-6">
                You'll receive a confirmation email shortly with all the details.
              </p>
              
              {/* Appointment Details */}
              {appointmentDetails && (
                <div className="bg-green-50 rounded-lg p-4 mb-6 text-left">
                  <h4 className="font-medium text-green-800 mb-2">Appointment Details:</h4>
                  <div className="text-sm text-green-700 space-y-1">
                    <p><span className="font-medium">Treatment:</span> {appointmentDetails.treatment}</p>
                    <p><span className="font-medium">Date:</span> {appointmentDetails.date}</p>
                    <p><span className="font-medium">Time:</span> {appointmentDetails.time}</p>
                    {appointmentDetails.appointment_id && (
                      <p><span className="font-medium">Booking ID:</span> #{appointmentDetails.appointment_id}</p>
                    )}
                  </div>
                </div>
              )}
              
              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={handleSuccessModalClose}
                  className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white font-semibold rounded-lg hover:from-green-700 hover:to-green-800 transition-all duration-200 shadow-md hover:shadow-lg"
                >
                  💬 Continue to Chat
                </button>
                <button
                  onClick={() => setShowSuccessModal(false)}
                  className="w-full px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors duration-200"
                >
                  Stay on this page
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