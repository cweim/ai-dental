import React, { useState, useEffect } from 'react';

interface ClinicSetting {
  id: number;
  setting_key: string;
  setting_value: string;
  setting_type: string;
  display_name: string;
  description: string;
  category: string;
  updated_at: string | null;
}

interface SettingCategory {
  category: string;
  settings: ClinicSetting[];
}

const ClinicSettings: React.FC = () => {
  const [settings, setSettings] = useState<ClinicSetting[]>([]);
  const [groupedSettings, setGroupedSettings] = useState<SettingCategory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editingSettings, setEditingSettings] = useState<{[key: string]: string}>({});
  const [showNewSettingModal, setShowNewSettingModal] = useState(false);
  const [newSetting, setNewSetting] = useState({
    setting_key: '',
    setting_value: '',
    setting_type: 'text',
    display_name: '',
    description: '',
    category: 'general'
  });

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const categoryOrder = ['general', 'contact', 'email', 'review'];
  const categoryDisplayNames: {[key: string]: string} = {
    general: '🏥 General Information',
    contact: '📞 Contact Details', 
    email: '📧 Email Settings',
    review: '⭐ Review & Feedback'
  };

  const settingTypes = [
    { value: 'text', label: 'Text' },
    { value: 'email', label: 'Email' },
    { value: 'phone', label: 'Phone' },
    { value: 'url', label: 'URL' },
    { value: 'textarea', label: 'Long Text' }
  ];

  useEffect(() => {
    fetchSettings();
  }, []);

  useEffect(() => {
    // Group settings by category
    const grouped = categoryOrder.reduce((acc: SettingCategory[], category) => {
      const categorySettings = settings.filter(s => s.category === category);
      if (categorySettings.length > 0) {
        acc.push({
          category,
          settings: categorySettings.sort((a, b) => a.display_name.localeCompare(b.display_name))
        });
      }
      return acc;
    }, []);
    
    setGroupedSettings(grouped);
  }, [settings]);

  const fetchSettings = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/clinic/settings`);
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
        
        // Initialize editing state with current values
        const editingState: {[key: string]: string} = {};
        data.forEach((setting: ClinicSetting) => {
          editingState[setting.setting_key] = setting.setting_value;
        });
        setEditingSettings(editingState);
      } else {
        alert('Failed to fetch clinic settings');
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
      alert('Error fetching clinic settings');
    } finally {
      setIsLoading(false);
    }
  };

  const updateSetting = async (settingKey: string, newValue: string) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/clinic/settings/${settingKey}?setting_value=${encodeURIComponent(newValue)}`,
        { method: 'PUT' }
      );

      if (response.ok) {
        // Update local state
        setSettings(prev => prev.map(setting => 
          setting.setting_key === settingKey 
            ? { ...setting, setting_value: newValue, updated_at: new Date().toISOString() }
            : setting
        ));
        
        // Show success feedback
        const settingName = settings.find(s => s.setting_key === settingKey)?.display_name;
        alert(`✅ ${settingName} updated successfully!`);
      } else {
        alert('Failed to update setting');
      }
    } catch (error) {
      console.error('Error updating setting:', error);
      alert('Error updating setting');
    }
  };

  const handleSettingChange = (settingKey: string, value: string) => {
    setEditingSettings(prev => ({
      ...prev,
      [settingKey]: value
    }));
  };

  const handleSettingBlur = (settingKey: string) => {
    const currentValue = settings.find(s => s.setting_key === settingKey)?.setting_value || '';
    const newValue = editingSettings[settingKey] || '';
    
    if (newValue !== currentValue && newValue.trim() !== '') {
      updateSetting(settingKey, newValue.trim());
    }
  };

  const createNewSetting = async () => {
    if (!newSetting.setting_key || !newSetting.display_name || !newSetting.setting_value) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      const params = new URLSearchParams({
        setting_key: newSetting.setting_key,
        setting_value: newSetting.setting_value,
        setting_type: newSetting.setting_type,
        display_name: newSetting.display_name,
        description: newSetting.description,
        category: newSetting.category
      });

      const response = await fetch(`${API_BASE_URL}/api/admin/clinic/settings?${params}`, {
        method: 'POST'
      });

      if (response.ok) {
        fetchSettings(); // Refresh the list
        setShowNewSettingModal(false);
        setNewSetting({
          setting_key: '',
          setting_value: '',
          setting_type: 'text',
          display_name: '',
          description: '',
          category: 'general'
        });
        alert('✅ New setting created successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to create setting: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating setting:', error);
      alert('Error creating setting');
    }
  };

  const renderSettingInput = (setting: ClinicSetting) => {
    const value = editingSettings[setting.setting_key] || '';
    const inputClasses = "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent";

    switch (setting.setting_type) {
      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => handleSettingChange(setting.setting_key, e.target.value)}
            onBlur={() => handleSettingBlur(setting.setting_key)}
            className={`${inputClasses} resize-none`}
            rows={3}
            placeholder={setting.description}
          />
        );
      case 'email':
        return (
          <input
            type="email"
            value={value}
            onChange={(e) => handleSettingChange(setting.setting_key, e.target.value)}
            onBlur={() => handleSettingBlur(setting.setting_key)}
            className={inputClasses}
            placeholder={setting.description}
          />
        );
      case 'phone':
        return (
          <input
            type="tel"
            value={value}
            onChange={(e) => handleSettingChange(setting.setting_key, e.target.value)}
            onBlur={() => handleSettingBlur(setting.setting_key)}
            className={inputClasses}
            placeholder={setting.description}
          />
        );
      case 'url':
        return (
          <input
            type="url"
            value={value}
            onChange={(e) => handleSettingChange(setting.setting_key, e.target.value)}
            onBlur={() => handleSettingBlur(setting.setting_key)}
            className={inputClasses}
            placeholder={setting.description}
          />
        );
      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleSettingChange(setting.setting_key, e.target.value)}
            onBlur={() => handleSettingBlur(setting.setting_key)}
            className={inputClasses}
            placeholder={setting.description}
          />
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            🏥 Clinic Settings
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Manage your clinic information used in emails and throughout the system
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <button
            onClick={() => setShowNewSettingModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-all duration-200"
          >
            ➕ Add New Setting
          </button>
        </div>
      </div>

      {/* Settings grouped by category */}
      {isLoading ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="inline-flex items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
            <div className="text-gray-500 text-lg">Loading settings...</div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {groupedSettings.map((group) => (
            <div key={group.category} className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  {categoryDisplayNames[group.category] || group.category}
                </h3>
                {group.category === 'review' && (
                  <p className="text-sm text-gray-600 mt-1">
                    💡 Google Review Link will be automatically included in follow-up emails
                  </p>
                )}
              </div>
              
              <div className="p-6 space-y-6">
                {group.settings.map((setting) => (
                  <div key={setting.setting_key} className="space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {setting.display_name}
                          {setting.setting_key === 'google_review_url' && (
                            <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                              Used in Follow-up Emails
                            </span>
                          )}
                        </label>
                        {setting.description && (
                          <p className="text-xs text-gray-500 mb-2">{setting.description}</p>
                        )}
                        {renderSettingInput(setting)}
                      </div>
                      <div className="ml-4 flex-shrink-0">
                        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                          {setting.setting_type}
                        </span>
                      </div>
                    </div>
                    
                    {setting.updated_at && (
                      <p className="text-xs text-gray-400">
                        Last updated: {new Date(setting.updated_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Help Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 How Settings Work</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p><strong>🏥 General:</strong> Basic clinic information used throughout the system</p>
          <p><strong>📞 Contact:</strong> Phone numbers, email, and address for patient communications</p>
          <p><strong>📧 Email:</strong> Settings that control email automation timing and behavior</p>
          <p><strong>⭐ Review:</strong> Google Review link automatically included in follow-up emails</p>
          <p><strong>💾 Auto-save:</strong> Changes are saved automatically when you click outside an input field</p>
        </div>
      </div>

      {/* New Setting Modal */}
      {showNewSettingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-lg w-full shadow-2xl">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-bold text-gray-900">Add New Setting</h3>
              <button
                onClick={() => setShowNewSettingModal(false)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-full"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Setting Key *</label>
                <input
                  type="text"
                  value={newSetting.setting_key}
                  onChange={(e) => setNewSetting({...newSetting, setting_key: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., clinic_website"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Display Name *</label>
                <input
                  type="text"
                  value={newSetting.display_name}
                  onChange={(e) => setNewSetting({...newSetting, display_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Clinic Website"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Value *</label>
                <input
                  type="text"
                  value={newSetting.setting_value}
                  onChange={(e) => setNewSetting({...newSetting, setting_value: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., https://www.example.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select
                    value={newSetting.setting_type}
                    onChange={(e) => setNewSetting({...newSetting, setting_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {settingTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={newSetting.category}
                    onChange={(e) => setNewSetting({...newSetting, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {categoryOrder.map(category => (
                      <option key={category} value={category}>
                        {categoryDisplayNames[category]?.replace(/^[🏥📞📧⭐]\s/, '') || category}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newSetting.description}
                  onChange={(e) => setNewSetting({...newSetting, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={2}
                  placeholder="Optional description or help text"
                />
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowNewSettingModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={createNewSetting}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Create Setting
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClinicSettings;