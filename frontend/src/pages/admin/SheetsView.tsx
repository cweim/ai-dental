import React, { useState, useEffect } from 'react';

interface BookingRecord {
  id: string;
  patientName: string;
  email: string;
  phone: string;
  date: string;
  time: string;
  treatment: string;
  price: string;
  duration: string;
  notes: string;
  adminNotes?: string;
  status: 'confirmed' | 'completed' | 'cancelled';
  createdAt: string;
}

interface PaginationInfo {
  page: number;
  limit: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

const SheetsView: React.FC = () => {
  const [bookings, setBookings] = useState<BookingRecord[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    limit: 50,
    total_count: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'treatment'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedBooking, setSelectedBooking] = useState<BookingRecord | null>(null);
  const [editingNotes, setEditingNotes] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Fetch real bookings from database
  const fetchBookings = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '50',
        search: searchTerm,
        status: statusFilter,
        sort_by: sortBy,
        sort_order: sortOrder
      });

      const response = await fetch(`${API_BASE_URL}/api/admin/sheets/bookings?${params}`);
      if (!response.ok) {
        throw new Error('Failed to fetch bookings');
      }

      const data = await response.json();
      setBookings(data.bookings);
      setPagination(data.pagination);
    } catch (error) {
      console.error('Error fetching bookings:', error);
      setBookings([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch data on component mount and when filters change
  useEffect(() => {
    fetchBookings();
  }, [currentPage, searchTerm, statusFilter, sortBy, sortOrder]);

  // Reset to first page when filters change
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1);
    }
  }, [searchTerm, statusFilter, sortBy, sortOrder]);

  // Modal and notes management
  const handleSelectBooking = (booking: BookingRecord) => {
    setSelectedBooking(booking);
    setEditingNotes(booking.adminNotes || '');
  };

  const handleCloseModal = () => {
    setSelectedBooking(null);
    setEditingNotes('');
  };

  const handleSaveNotes = async () => {
    if (selectedBooking) {
      try {
        // Save to backend
        const response = await fetch(`${API_BASE_URL}/api/admin/appointments/${selectedBooking.id}/notes`, {
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
          const updatedBookings = bookings.map(booking => 
            booking.id === selectedBooking.id 
              ? {
                  ...booking,
                  adminNotes: editingNotes.trim() || undefined
                }
              : booking
          );
          setBookings(updatedBookings);
          setSelectedBooking({
            ...selectedBooking,
            adminNotes: editingNotes.trim() || undefined
          });
        } else {
          console.error('Failed to save admin notes to backend');
        }
      } catch (error) {
        console.error('Error saving admin notes:', error);
      }
    }
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (timeString: string) => {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  const exportToCSV = () => {
    const headers = ['ID', 'Patient Name', 'Email', 'Phone', 'Date', 'Time', 'Treatment', 'Price', 'Duration', 'Patient Notes', 'Admin Notes', 'Status', 'Created At'];
    const csvContent = [
      headers.join(','),
      ...bookings.map(booking => [
        booking.id,
        `"${booking.patientName}"`,
        booking.email,
        booking.phone,
        booking.date,
        booking.time,
        `"${booking.treatment}"`,
        booking.price,
        booking.duration,
        `"${booking.notes}"`,
        `"${booking.adminNotes || ''}"`,
        booking.status,
        new Date(booking.createdAt).toLocaleString()
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'booking_logs.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            📋 Booking Logs
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            All appointment bookings with detailed records
          </p>
        </div>
        <div className="mt-4 flex space-x-2 md:ml-4 md:mt-0">
          <button
            onClick={exportToCSV}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            📁 Export CSV
          </button>
          <button 
            onClick={fetchBookings}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            🔄 Refresh Data
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              placeholder="Patient name, email, or treatment..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Status</option>
              <option value="confirmed">Confirmed</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'name' | 'treatment')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="date">Date</option>
              <option value="name">Patient Name</option>
              <option value="treatment">Treatment</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Order
            </label>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500">Total Bookings</div>
          <div className="text-2xl font-bold text-gray-900">{pagination.total_count}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500">Confirmed</div>
          <div className="text-2xl font-bold text-green-600">
            {bookings.filter(b => b.status === 'confirmed').length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500">Cancelled</div>
          <div className="text-2xl font-bold text-red-600">
            {bookings.filter(b => b.status === 'cancelled').length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500">Completed</div>
          <div className="text-2xl font-bold text-blue-600">
            {bookings.filter(b => b.status === 'completed').length}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Appointment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Treatment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {bookings.map((booking) => (
                <tr 
                  key={booking.id} 
                  className="hover:bg-gray-50 cursor-pointer transition-colors duration-200"
                  onClick={() => handleSelectBooking(booking)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {booking.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{booking.patientName}</div>
                    {booking.notes && (
                      <div className="text-sm text-gray-500 truncate max-w-xs" title={booking.notes}>
                        {booking.notes}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{booking.email}</div>
                    <div className="text-sm text-gray-500">{booking.phone}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{formatDate(booking.date)}</div>
                    <div className="text-sm text-gray-500">{formatTime(booking.time)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{booking.treatment}</div>
                    <div className="text-sm text-gray-500">{booking.price} • {booking.duration}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(booking.status)}`}>
                      {booking.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(booking.createdAt).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {pagination.total_pages > 1 && (
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 rounded-lg shadow">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={!pagination.has_prev}
              className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                pagination.has_prev 
                  ? 'text-gray-700 bg-white hover:bg-gray-50' 
                  : 'text-gray-400 bg-gray-100 cursor-not-allowed'
              }`}
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, pagination.total_pages))}
              disabled={!pagination.has_next}
              className={`ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                pagination.has_next 
                  ? 'text-gray-700 bg-white hover:bg-gray-50' 
                  : 'text-gray-400 bg-gray-100 cursor-not-allowed'
              }`}
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{((currentPage - 1) * pagination.limit) + 1}</span> to{' '}
                <span className="font-medium">
                  {Math.min(currentPage * pagination.limit, pagination.total_count)}
                </span>{' '}
                of <span className="font-medium">{pagination.total_count}</span> results
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={!pagination.has_prev}
                  className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium ${
                    pagination.has_prev 
                      ? 'text-gray-500 bg-white hover:bg-gray-50' 
                      : 'text-gray-300 bg-gray-100 cursor-not-allowed'
                  }`}
                >
                  <span className="sr-only">Previous</span>
                  <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </button>
                
                {/* Page numbers */}
                {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                  const pageNum = Math.max(1, Math.min(
                    currentPage - 2 + i,
                    pagination.total_pages - 4 + i
                  ));
                  if (pageNum > pagination.total_pages) return null;
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        currentPage === pageNum
                          ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, pagination.total_pages))}
                  disabled={!pagination.has_next}
                  className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium ${
                    pagination.has_next 
                      ? 'text-gray-500 bg-white hover:bg-gray-50' 
                      : 'text-gray-300 bg-gray-100 cursor-not-allowed'
                  }`}
                >
                  <span className="sr-only">Next</span>
                  <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}

      {bookings.length === 0 && !isLoading && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="text-gray-500 text-lg">No bookings found matching your criteria.</div>
        </div>
      )}

      {isLoading && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="inline-flex items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mr-3"></div>
            <div className="text-gray-500 text-lg">Loading bookings...</div>
          </div>
        </div>
      )}

      {/* Booking Details Modal */}
      {selectedBooking && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-white rounded-xl max-w-lg w-full shadow-2xl border border-gray-200 overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Booking Details</h3>
                  <p className="text-sm text-gray-600">{selectedBooking.id} • {selectedBooking.patientName}</p>
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
                  <p className="text-sm font-semibold text-gray-900">{selectedBooking.treatment}</p>
                  <p className="text-xs text-gray-500">{selectedBooking.price} • {selectedBooking.duration}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedBooking.status)}`}>
                  {selectedBooking.status}
                </span>
              </div>

              {/* Date, Time & Contact Grid */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-gray-500 text-xs font-medium">Date & Time</p>
                  <p className="text-gray-900 font-medium">{formatDate(selectedBooking.date)}</p>
                  <p className="text-gray-600">{formatTime(selectedBooking.time)}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs font-medium">Contact</p>
                  <p className="text-gray-900 font-medium text-xs">{selectedBooking.email}</p>
                  <p className="text-gray-600 text-xs">{selectedBooking.phone}</p>
                </div>
              </div>

              {/* Patient Notes */}
              {selectedBooking.notes && (
                <div>
                  <p className="text-gray-500 text-xs font-medium mb-1">Patient Notes</p>
                  <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded border">{selectedBooking.notes}</p>
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

              {/* Booking Info */}
              <div className="pt-2 border-t border-gray-100">
                <div className="flex justify-between text-xs text-gray-500">
                  <span>ID: {selectedBooking.id}</span>
                  <span>Created: {new Date(selectedBooking.createdAt).toLocaleDateString()}</span>
                </div>
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

export default SheetsView;