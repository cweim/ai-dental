import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer, View } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

interface AppointmentEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  resource: {
    patientName: string;
    patientEmail: string;
    patientPhone: string;
    treatment: string;
    status: 'confirmed' | 'completed' | 'cancelled';
    notes?: string;
    adminNotes?: string;
  };
}

const CalendarView: React.FC = () => {
  const [events, setEvents] = useState<AppointmentEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<AppointmentEvent | null>(null);
  const [currentView, setCurrentView] = useState<View>('month');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [editingNotes, setEditingNotes] = useState('');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Load real appointments from database
  useEffect(() => {
    const fetchAppointments = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/calendar/events`);
        if (!response.ok) {
          throw new Error('Failed to fetch appointments');
        }
        const data = await response.json();
        
        // Transform API data to calendar events
        const events: AppointmentEvent[] = data.events.map((event: any) => ({
          id: event.id,
          title: event.title,
          start: new Date(event.start),
          end: new Date(event.end),
          resource: {
            patientName: event.resource.patientName,
            patientEmail: event.resource.patientEmail,
            patientPhone: event.resource.patientPhone,
            treatment: event.resource.treatment,
            status: event.resource.status as 'confirmed' | 'completed' | 'cancelled',
            notes: event.resource.notes,
            adminNotes: event.resource.adminNotes
          }
        }));
        
        setEvents(events);
      } catch (error) {
        console.error('Error fetching appointments:', error);
        // Set empty array on error instead of mock data
        setEvents([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAppointments();
  }, [API_BASE_URL, refreshTrigger]);

  const eventStyleGetter = (event: AppointmentEvent) => {
    let backgroundColor = '#3b82f6'; // blue
    
    switch (event.resource.status) {
      case 'confirmed':
        backgroundColor = '#10b981'; // green
        break;
      case 'completed':
        backgroundColor = '#6b7280'; // gray
        break;
      case 'cancelled':
        backgroundColor = '#ef4444'; // red
        break;
    }
    
    return {
      style: {
        backgroundColor,
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block'
      }
    };
  };

  const handleSelectEvent = (event: AppointmentEvent) => {
    setSelectedEvent(event);
    setEditingNotes(event.resource.adminNotes || '');
  };

  const handleCloseModal = () => {
    setSelectedEvent(null);
    setEditingNotes('');
  };

  const handleSaveNotes = async () => {
    if (selectedEvent) {
      try {
        // Save to backend
        const response = await fetch(`${API_BASE_URL}/api/admin/appointments/${selectedEvent.id}/notes`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            admin_notes: editingNotes.trim()
          })
        });

        if (response.ok) {
          // Update local state only if backend save succeeds
          const updatedEvents = events.map(event => 
            event.id === selectedEvent.id 
              ? {
                  ...event,
                  resource: {
                    ...event.resource,
                    adminNotes: editingNotes.trim() || undefined
                  }
                }
              : event
          );
          setEvents(updatedEvents);
          setSelectedEvent({
            ...selectedEvent,
            resource: {
              ...selectedEvent.resource,
              adminNotes: editingNotes.trim() || undefined
            }
          });
        } else {
          console.error('Failed to save admin notes to backend');
        }
      } catch (error) {
        console.error('Error saving admin notes:', error);
      }
    }
  };

  const formatTime = (date: Date) => {
    return moment(date).format('h:mm A');
  };

  const formatDate = (date: Date) => {
    return moment(date).format('MMMM D, YYYY');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const exportBookingLogs = () => {
    const csv = events.map(event => [
      event.id,
      event.resource.patientName,
      event.resource.patientEmail,
      event.resource.patientPhone,
      event.resource.treatment,
      moment(event.start).format('YYYY-MM-DD'),
      moment(event.start).format('HH:mm'),
      moment(event.end).format('HH:mm'),
      event.resource.status,
      event.resource.notes || '',
      event.resource.adminNotes || ''
    ]);
    
    const csvContent = [
      ['ID', 'Patient Name', 'Email', 'Phone', 'Treatment', 'Date', 'Start Time', 'End Time', 'Status', 'Patient Notes', 'Admin Notes'],
      ...csv
    ].map(row => row.map(field => `"${field}"`).join(',')).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `booking-logs-${moment().format('YYYY-MM-DD')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Enhanced Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="md:flex md:items-center md:justify-between">
          <div className="min-w-0 flex-1">
            <h2 className="text-3xl font-bold leading-7 text-gray-900 sm:truncate sm:text-4xl sm:tracking-tight flex items-center">
              📅 <span className="ml-3">Appointment Calendar</span>
            </h2>
            <p className="mt-2 text-lg text-gray-600">
              Manage your dental practice appointments - {events.length} total appointments
            </p>
          </div>
          <div className="mt-6 flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3 md:ml-4 md:mt-0">
            {/* Refresh Button */}
            <button
              onClick={() => setRefreshTrigger(prev => prev + 1)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-all duration-200 shadow-md hover:shadow-lg"
            >
              🔄 Refresh
            </button>
            
            {/* Export Button */}
            <button
              onClick={exportBookingLogs}
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 transition-all duration-200 shadow-md hover:shadow-lg"
            >
              📊 Export Logs
            </button>
            
            {/* View Toggle Buttons */}
            <div className="flex space-x-2 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setCurrentView('month')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                  currentView === 'month'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-gray-700 hover:bg-white hover:shadow-sm'
                }`}
              >
                Month
              </button>
              <button
                onClick={() => setCurrentView('week')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                  currentView === 'week'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-gray-700 hover:bg-white hover:shadow-sm'
                }`}
              >
                Week
              </button>
              <button
                onClick={() => setCurrentView('day')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                  currentView === 'day'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-gray-700 hover:bg-white hover:shadow-sm'
                }`}
              >
                Day
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Appointment Status Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <span className="mr-2">🎯</span>
          Appointment Status ({currentView === 'month' ? 'This Month' : currentView === 'week' ? 'This Week' : 'Today'})
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-xl border border-green-200">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-green-500 rounded-full mr-3"></div>
              <span className="text-sm font-semibold text-green-800">Confirmed</span>
            </div>
            <span className="text-2xl font-bold text-green-600">
              {events.filter(e => {
                const eventDate = moment(e.start);
                const currentDate = moment(selectedDate);
                if (currentView === 'month') {
                  return e.resource.status === 'confirmed' && eventDate.isSame(currentDate, 'month');
                } else if (currentView === 'week') {
                  return e.resource.status === 'confirmed' && eventDate.isSame(currentDate, 'week');
                } else {
                  return e.resource.status === 'confirmed' && eventDate.isSame(currentDate, 'day');
                }
              }).length}
            </span>
          </div>
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl border border-gray-200">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-gray-500 rounded-full mr-3"></div>
              <span className="text-sm font-semibold text-gray-800">Completed</span>
            </div>
            <span className="text-2xl font-bold text-gray-600">
              {events.filter(e => {
                const eventDate = moment(e.start);
                const currentDate = moment(selectedDate);
                if (currentView === 'month') {
                  return e.resource.status === 'completed' && eventDate.isSame(currentDate, 'month');
                } else if (currentView === 'week') {
                  return e.resource.status === 'completed' && eventDate.isSame(currentDate, 'week');
                } else {
                  return e.resource.status === 'completed' && eventDate.isSame(currentDate, 'day');
                }
              }).length}
            </span>
          </div>
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-red-50 to-red-100 rounded-xl border border-red-200">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-red-500 rounded-full mr-3"></div>
              <span className="text-sm font-semibold text-red-800">Cancelled</span>
            </div>
            <span className="text-2xl font-bold text-red-600">
              {events.filter(e => {
                const eventDate = moment(e.start);
                const currentDate = moment(selectedDate);
                if (currentView === 'month') {
                  return e.resource.status === 'cancelled' && eventDate.isSame(currentDate, 'month');
                } else if (currentView === 'week') {
                  return e.resource.status === 'cancelled' && eventDate.isSame(currentDate, 'week');
                } else {
                  return e.resource.status === 'cancelled' && eventDate.isSame(currentDate, 'day');
                }
              }).length}
            </span>
          </div>
        </div>
      </div>

      {/* Enhanced Calendar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <span className="mr-2">📅</span>
              Calendar View
              {isLoading && (
                <div className="ml-3 flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-sm text-gray-500">Loading...</span>
                </div>
              )}
            </h3>
            
            {/* Month Navigation */}
            <div className="flex items-center space-x-4">
              <span className="text-lg font-semibold text-gray-700">
                {moment(selectedDate).format('MMMM YYYY')}
              </span>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setSelectedDate(moment(selectedDate).subtract(1, 'month').toDate())}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-full transition-all duration-200"
                  title="Previous Month"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button
                  onClick={() => setSelectedDate(new Date())}
                  className="px-3 py-1 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-all duration-200"
                  title="Go to Today"
                >
                  Today
                </button>
                <button
                  onClick={() => setSelectedDate(moment(selectedDate).add(1, 'month').toDate())}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-full transition-all duration-200"
                  title="Next Month"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div style={{ height: '650px' }}>
            <Calendar
              localizer={localizer}
              events={events}
              startAccessor="start"
              endAccessor="end"
              view={currentView}
              date={selectedDate}
              onNavigate={setSelectedDate}
              onView={setCurrentView}
              onSelectEvent={handleSelectEvent}
              eventPropGetter={eventStyleGetter}
              popup
              views={['month', 'week', 'day']}
              step={30}
              showMultiDayTimes
              toolbar={false}
              style={{
                fontFamily: 'Inter, system-ui, sans-serif'
              }}
            />
          </div>
        </div>
      </div>

      {/* Quick Stats Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <span className="mr-2">📊</span>
          Quick Stats
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {events.filter(e => moment(e.start).isSame(moment(), 'day')).length}
            </div>
            <div className="text-sm font-semibold text-blue-800">Today's Appointments</div>
          </div>
          <div className="text-center p-4 bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-xl">
            <div className="text-3xl font-bold text-indigo-600 mb-2">
              {events.filter(e => moment(e.start).isSame(moment(), 'week')).length}
            </div>
            <div className="text-sm font-semibold text-indigo-800">This Week</div>
          </div>
          <div className="text-center p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {events.filter(e => moment(e.start).isSame(moment(), 'month')).length}
            </div>
            <div className="text-sm font-semibold text-purple-800">This Month</div>
          </div>
        </div>
      </div>

      {/* Appointment Details Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-white rounded-xl max-w-lg w-full shadow-2xl border border-gray-200 overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Appointment Details</h3>
                  <p className="text-sm text-gray-600">{selectedEvent.resource.patientName}</p>
                </div>
                <button
                  onClick={handleCloseModal}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded-full transition-colors duration-200"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="px-6 py-4 space-y-4">
              {/* Treatment & Status Row */}
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm font-semibold text-gray-900">{selectedEvent.resource.treatment}</p>
                  <p className="text-xs text-gray-500">
                    {formatTime(selectedEvent.start)} - {formatTime(selectedEvent.end)}
                  </p>
                </div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedEvent.resource.status)}`}>
                  {selectedEvent.resource.status}
                </span>
              </div>

              {/* Date & Contact Grid */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-gray-500 text-xs font-medium">Date</p>
                  <p className="text-gray-900 font-medium">{formatDate(selectedEvent.start)}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs font-medium">Contact</p>
                  <p className="text-gray-900 font-medium text-xs">{selectedEvent.resource.patientEmail}</p>
                  <p className="text-gray-600 text-xs">{selectedEvent.resource.patientPhone}</p>
                </div>
              </div>

              {/* Patient Notes */}
              {selectedEvent.resource.notes && (
                <div>
                  <p className="text-gray-500 text-xs font-medium mb-1">Patient Notes</p>
                  <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded border">{selectedEvent.resource.notes}</p>
                </div>
              )}

              {/* Admin Notes - Direct Edit */}
              <div>
                <label className="block text-gray-500 text-xs font-medium mb-1">Admin Notes</label>
                <textarea
                  value={editingNotes}
                  onChange={(e) => setEditingNotes(e.target.value)}
                  onBlur={handleSaveNotes}
                  placeholder="Add notes for future appointments..."
                  rows={3}
                  className="w-full p-2 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent resize-none bg-white"
                />
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
              <button
                onClick={handleCloseModal}
                className="w-full py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors duration-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarView;