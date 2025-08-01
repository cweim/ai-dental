import React from 'react';
import { useNavigate } from 'react-router-dom';
import landingImage from './landing_image.jpg';

const Landing: React.FC = () => {
  const navigate = useNavigate();
  
  const handleNavigation = (path: string) => {
    navigate(path);
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
            <a href="#" className="text-blue-600 font-medium text-sm">• Home</a>
            <a href="#" className="text-gray-700 hover:text-gray-900 text-sm transition-colors">Doctors</a>
            <a href="#" className="text-gray-700 hover:text-gray-900 text-sm transition-colors">Price list</a>
            <a href="#" className="text-gray-700 hover:text-gray-900 text-sm transition-colors">Contact</a>
            <a href="#" className="text-gray-700 hover:text-gray-900 text-sm transition-colors">Team</a>
          </div>

          <div className="hidden md:block">
            <span className="text-gray-700 text-sm">Eng</span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-16 items-center min-h-[calc(100vh-200px)]">
            
            {/* Left Content */}
            <div className="text-gray-900 order-2 lg:order-1">
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-light leading-tight mb-8">
                Your smile
                <br />
                comes first
              </h1>
            </div>

            {/* Right Content - Hero Image Placeholder & Practice Hours */}
            <div className="order-1 lg:order-2 relative">
              {/* Hero Image Placeholder */}
              {/* Hero Image */}
              <div className="bg-blue-50/80 backdrop-blur-sm rounded-3xl overflow-hidden mb-6 aspect-[4/3] flex items-center justify-center border border-blue-200">
                <img
                  src={landingImage}
                  alt="SmileCare Dental Clinic - Modern dental office"
                  className="object-cover w-full h-full"
                />
              </div>


              {/* Practice Hours Card */}
              <div className="bg-blue-50/80 backdrop-blur-sm rounded-2xl p-6 border border-blue-200">
                <h3 className="text-gray-900 font-medium text-lg mb-4">Practice Hours</h3>
                <div className="space-y-3 text-gray-700 text-sm">
                  <div className="flex justify-between">
                    <span>Monday—Tuesday:</span>
                    <span className="text-gray-900">09:00—21:00</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Friday:</span>
                    <span className="text-gray-900">09:00—19:00</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Saturday:</span>
                    <span className="text-gray-900">11:00—16:00</span>
                  </div>
                </div>
                
                <div className="mt-6 pt-4 border-t border-blue-200">
                  <div className="bg-blue-100/80 backdrop-blur-sm rounded-xl p-3 border border-blue-300">
                    <div className="text-gray-900 font-medium text-sm">Today is Monday</div>
                    <div className="text-gray-700 text-xs mt-1">3:21 pm</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Cards Section */}
      <div className="relative z-10 px-4 sm:px-6 lg:px-8 pb-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Chat with AI Button Card */}
            <div 
              onClick={() => handleNavigation('/chat')}
              className="bg-blue-50/80 backdrop-blur-sm rounded-2xl p-6 border border-blue-200 hover:bg-blue-100/80 transition-all duration-300 cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-gray-900 text-xl font-medium mb-2">Chat with AI</h3>
                  <p className="text-gray-700 text-sm leading-relaxed">Get instant answers and assistance for all your dental questions</p>
                </div>
                <div className="ml-4 group-hover:translate-x-1 transition-transform duration-300">
                  <div className="w-6 h-6 text-gray-600">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8.59 16.59L13.17 12L8.59 7.41L10 6l6 6-6 6-1.41-1.41z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Book Appointment Button Card */}
            <div 
              onClick={() => handleNavigation('/appointments')}
              className="bg-blue-50/80 backdrop-blur-sm rounded-2xl p-6 border border-blue-200 hover:bg-blue-100/80 transition-all duration-300 cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-gray-900 text-xl font-medium mb-2">Book Appointment</h3>
                  <p className="text-gray-700 text-sm leading-relaxed">Schedule your visit with our experienced dental professionals</p>
                </div>
                <div className="ml-4 group-hover:translate-x-1 transition-transform duration-300">
                  <div className="w-6 h-6 text-gray-600">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8.59 16.59L13.17 12L8.59 7.41L10 6l6 6-6 6-1.41-1.41z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Cancel Booking Button Card */}
            <div 
              onClick={() => handleNavigation('/cancel-appointment')}
              className="bg-blue-50/80 backdrop-blur-sm rounded-2xl p-6 border border-blue-200 hover:bg-blue-100/80 transition-all duration-300 cursor-pointer group sm:col-span-2 lg:col-span-1"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-gray-900 text-xl font-medium mb-2">Cancel Booking</h3>
                  <p className="text-gray-700 text-sm leading-relaxed">Manage your existing appointments and reschedule if needed</p>
                </div>
                <div className="ml-4 group-hover:translate-x-1 transition-transform duration-300">
                  <div className="w-6 h-6 text-gray-600">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8.59 16.59L13.17 12L8.59 7.41L10 6l6 6-6 6-1.41-1.41z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Services Section */}
      <div className="relative z-10 px-4 sm:px-6 lg:px-8 pb-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-blue-50/60 backdrop-blur-sm rounded-2xl p-8 border border-blue-200">
            <h3 className="text-gray-900 font-medium text-xl mb-6 text-center">Our Dental Services</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-blue-50/80 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-blue-100/80 transition-all duration-300 cursor-pointer border border-blue-200">
                <div className="text-2xl mb-3">🦷</div>
                <div className="text-gray-900 text-sm font-medium">General Care</div>
                <div className="text-gray-600 text-xs mt-1">Routine checkups</div>
              </div>
              <div className="bg-blue-50/80 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-blue-100/80 transition-all duration-300 cursor-pointer border border-blue-200">
                <div className="text-2xl mb-3">✨</div>
                <div className="text-gray-900 text-sm font-medium">Whitening</div>
                <div className="text-gray-600 text-xs mt-1">Brighten your smile</div>
              </div>
              <div className="bg-blue-50/80 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-blue-100/80 transition-all duration-300 cursor-pointer border border-blue-200">
                <div className="text-2xl mb-3">🔧</div>
                <div className="text-gray-900 text-sm font-medium">Repairs</div>
                <div className="text-gray-600 text-xs mt-1">Fillings & fixes</div>
              </div>
              <div className="bg-blue-50/80 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-blue-100/80 transition-all duration-300 cursor-pointer border border-blue-200">
                <div className="text-2xl mb-3">👑</div>
                <div className="text-gray-900 text-sm font-medium">Crowns</div>
                <div className="text-gray-600 text-xs mt-1">Premium solutions</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Footer */}
      <div className="relative z-10 px-4 sm:px-6 lg:px-8 pb-8">
        <div className="max-w-7xl mx-auto text-center">
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
  );
};

export default Landing;