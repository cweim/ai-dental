import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Welcome to AI Dentist
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Book your dental appointment with ease
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto">
          <a
            href="/appointments"
            className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-lg hover:shadow-xl text-center"
          >
            <div className="text-2xl mb-2">📅</div>
            <div className="font-semibold">Book Appointment</div>
            <div className="text-sm opacity-90">Schedule your visit</div>
          </a>
          <a
            href="/chat"
            className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-4 rounded-xl hover:from-green-700 hover:to-green-800 transition-all duration-200 shadow-lg hover:shadow-xl text-center"
          >
            <div className="text-2xl mb-2">💬</div>
            <div className="font-semibold">Chat with AI</div>
            <div className="text-sm opacity-90">Get dental advice</div>
          </a>
          <a
            href="/cancel-appointment"
            className="bg-gradient-to-r from-red-600 to-red-700 text-white px-6 py-4 rounded-xl hover:from-red-700 hover:to-red-800 transition-all duration-200 shadow-lg hover:shadow-xl text-center"
          >
            <div className="text-2xl mb-2">🗑️</div>
            <div className="font-semibold">Cancel Appointment</div>
            <div className="text-sm opacity-90">Manage your bookings</div>
          </a>
        </div>
      </div>
    </div>
  );
};

export default Home;