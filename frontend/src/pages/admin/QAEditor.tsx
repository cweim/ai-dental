import React, { useState, useEffect } from 'react';

interface QAEntry {
  id: number;
  question: string;
  answer: string;
  category: string;
  source: string;
  source_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  embedding_vector?: string;
  confidence_threshold?: number;
  in_knowledge_base?: boolean;
}

interface ApiResponse {
  success: boolean;
  data?: any;
  error?: string;
}

const QAEditor: React.FC = () => {
  const [qaEntries, setQAEntries] = useState<QAEntry[]>([]);
  const [filteredEntries, setFilteredEntries] = useState<QAEntry[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [isEditing, setIsEditing] = useState(false);
  const [editingEntry, setEditingEntry] = useState<QAEntry | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [showQuickTest, setShowQuickTest] = useState(false);
  const [testQuery, setTestQuery] = useState('');
  const [selectedForKB, setSelectedForKB] = useState<number[]>([]);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Fetch QA entries from API
  const fetchQAEntries = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/qa`);
      if (!response.ok) {
        throw new Error('Failed to fetch QA entries');
      }
      
      const data = await response.json();
      setQAEntries(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch QA entries');
      console.error('Error fetching QA entries:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch categories from API
  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/qa/categories`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories || []);
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };


  // Test RAG search
  const testRAGSearch = async (query: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/qa/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          k: 5,
          threshold: 0.3  // Lower threshold for better results
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        console.error('RAG search failed:', response.status, response.statusText);
        return { query, results: [], error: `HTTP ${response.status}` };
      }
    } catch (err) {
      console.error('Error testing RAG search:', err);
      return { query, results: [], error: err instanceof Error ? err.message : 'Unknown error occurred' };
    }
  };


  // Load data on component mount
  useEffect(() => {
    fetchQAEntries();
    fetchCategories();
  }, []);

  // Filter entries based on search and category
  useEffect(() => {
    let filtered = qaEntries.filter(entry => {
      const matchesSearch = 
        entry.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
        entry.answer.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = categoryFilter === 'all' || entry.category === categoryFilter;
      
      return matchesSearch && matchesCategory;
    });

    setFilteredEntries(filtered);
  }, [qaEntries, searchTerm, categoryFilter]);

  const handleAddEntry = async (newEntry: Omit<QAEntry, 'id' | 'created_at' | 'updated_at'>) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/qa`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: newEntry.question,
          answer: newEntry.answer,
          category: newEntry.category,
          source: newEntry.source || 'user_defined',
          source_url: newEntry.source_url
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to create QA entry');
      }
      
      const createdEntry = await response.json();
      
      // Rebuild the RAG index after adding new entry
      try {
        const rebuildResponse = await fetch(`${API_BASE_URL}/api/chatbot/system/rebuild-index`, {
          method: 'POST'
        });
        
        if (!rebuildResponse.ok) {
          console.warn('Failed to rebuild RAG index after adding entry');
        } else {
          console.log('RAG index rebuilt successfully after adding entry');
        }
      } catch (rebuildErr) {
        console.warn('Error rebuilding RAG index:', rebuildErr);
      }
      
      setQAEntries([createdEntry, ...qaEntries]);
      setShowAddForm(false);
      
      // Refresh categories
      fetchCategories();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create QA entry');
      console.error('Error creating QA entry:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditEntry = async (updatedEntry: QAEntry) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/qa/${updatedEntry.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: updatedEntry.question,
          answer: updatedEntry.answer,
          category: updatedEntry.category
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to update QA entry');
      }
      
      // Rebuild the RAG index after editing entry
      try {
        const rebuildResponse = await fetch(`${API_BASE_URL}/api/chatbot/system/rebuild-index`, {
          method: 'POST'
        });
        
        if (!rebuildResponse.ok) {
          console.warn('Failed to rebuild RAG index after editing entry');
        } else {
          console.log('RAG index rebuilt successfully after editing entry');
        }
      } catch (rebuildErr) {
        console.warn('Error rebuilding RAG index:', rebuildErr);
      }
      
      // Refresh the QA entries
      fetchQAEntries();
      setIsEditing(false);
      setEditingEntry(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update QA entry');
      console.error('Error updating QA entry:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteEntry = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this Q&A entry?')) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/qa/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete QA entry');
      }
      
      // Rebuild the RAG index after deletion to ensure vector search is updated
      try {
        const rebuildResponse = await fetch(`${API_BASE_URL}/api/chatbot/system/rebuild-index`, {
          method: 'POST'
        });
        
        if (!rebuildResponse.ok) {
          console.warn('Failed to rebuild RAG index after deletion');
        } else {
          console.log('RAG index rebuilt successfully after deletion');
        }
      } catch (rebuildErr) {
        console.warn('Error rebuilding RAG index:', rebuildErr);
      }
      
      setQAEntries(qaEntries.filter(entry => entry.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete QA entry');
      console.error('Error deleting QA entry:', err);
    } finally {
      setLoading(false);
    }
  };

  // Rebuild vector database
  const rebuildVectorDatabase = async () => {
    setLoading(true);
    setError(null);
    setRebuildSuccess(null);
    
    try {
      console.log('Rebuilding FAISS vector database...');
      
      const response = await fetch(`${API_BASE_URL}/api/chatbot/system/rebuild-index`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to rebuild vector database');
      }
      
      const result = await response.json();
      console.log('Vector database rebuild successful:', result);
      
      setRebuildSuccess('Vector database rebuilt successfully! All QA pairs are now indexed for RAG search.');
      
      // Also refresh the QA entries to show updated status
      await fetchQAEntries();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to rebuild vector database');
      console.error('Error rebuilding vector database:', err);
    } finally {
      setLoading(false);
    }
  };

  const [ragTestResults, setRagTestResults] = useState<any>(null);
  const [testingRAG, setTestingRAG] = useState(false);
  const [rebuildSuccess, setRebuildSuccess] = useState<string | null>(null);


  const handleQuickTest = async () => {
    if (!testQuery.trim()) return;
    
    setTestingRAG(true);
    const results = await testRAGSearch(testQuery);
    setRagTestResults(results);
    setTestingRAG(false);
  };

  const QAForm: React.FC<{
    entry?: QAEntry;
    onSubmit: (entry: any) => void;
    onCancel: () => void;
  }> = ({ entry, onSubmit, onCancel }) => {
    // Default categories for dental clinic (matching database format with underscores)
    const defaultCategories = [
      'general', 'office_information', 'appointments', 'pricing', 'insurance', 
      'payment', 'emergency_care', 'preventive_care', 'dental_procedures', 'cosmetic_dentistry',
      'pediatric_dentistry', 'patient_care', 'first_visit', 'oral_hygiene', 'nutrition',
      'dental_conditions', 'restorative_dentistry', 'orthodontics', 'oral_surgery', 'post_treatment_care',
      'special_populations'
    ];
    
    const availableCategories = categories.length > 0 ? categories : defaultCategories;

    const [formData, setFormData] = useState({
      question: entry?.question || '',
      answer: entry?.answer || '',
      category: entry?.category || (availableCategories[0] || 'general'),
      source: entry?.source || 'user_defined',
      source_url: entry?.source_url || '',
      is_active: entry?.is_active ?? true
    });
    
    const [showAddCategory, setShowAddCategory] = useState(false);
    const [newCategoryInput, setNewCategoryInput] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit(entry ? { ...entry, ...formData } : formData);
    };

    const handleAddNewCategory = () => {
      if (newCategoryInput.trim() && !availableCategories.includes(newCategoryInput.trim())) {
        const newCategory = newCategoryInput.trim();
        setCategories([...categories, newCategory]);
        setFormData({ ...formData, category: newCategory });
        setNewCategoryInput('');
        setShowAddCategory(false);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {entry ? 'Edit Q&A Entry' : 'Add New Q&A Entry'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Question
              </label>
              <input
                type="text"
                value={formData.question}
                onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Answer
              </label>
              <textarea
                value={formData.answer}
                onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <div className="space-y-2">
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {availableCategories.map(category => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1).replace(/_/g, ' ')}
                    </option>
                  ))}
                </select>
                
                {!showAddCategory ? (
                  <button
                    type="button"
                    onClick={() => setShowAddCategory(true)}
                    className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                  >
                    ➕ Add new category
                  </button>
                ) : (
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newCategoryInput}
                      onChange={(e) => setNewCategoryInput(e.target.value)}
                      placeholder="e.g., preventive-care"
                      className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleAddNewCategory();
                        }
                        if (e.key === 'Escape') {
                          setShowAddCategory(false);
                          setNewCategoryInput('');
                        }
                      }}
                    />
                    <button
                      type="button"
                      onClick={handleAddNewCategory}
                      disabled={!newCategoryInput.trim()}
                      className="px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      Add
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowAddCategory(false);
                        setNewCategoryInput('');
                      }}
                      className="px-3 py-2 bg-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-400"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Source URL (optional)
              </label>
              <input
                type="url"
                value={formData.source_url}
                onChange={(e) => setFormData({ ...formData, source_url: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="https://example.com/reference"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="isActive"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="isActive" className="ml-2 block text-sm text-gray-900">
                Active (visible to chatbot)
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700"
              >
                {entry ? 'Update' : 'Add'} Entry
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            ✏️ Chatbot Q&A Manager
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Manage the knowledge base for your AI chatbot
          </p>
        </div>
        <div className="mt-4 flex flex-wrap gap-2 md:ml-4 md:mt-0">
          <button
            onClick={() => setShowQuickTest(true)}
            disabled={loading}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            🧪 RAG Test
          </button>
          <button
            onClick={rebuildVectorDatabase}
            disabled={loading}
            className="inline-flex items-center px-3 py-2 border border-blue-300 shadow-sm text-sm font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:opacity-50"
          >
            {loading ? '⏳' : '🔧'} Rebuild Vector DB
          </button>
          <button
            onClick={() => setShowAddForm(true)}
            disabled={loading}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
          >
            ➕ Add New Q&A
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-red-400">⚠️</div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
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

      {/* Success Alert */}
      {rebuildSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-green-400">✅</div>
            <div className="ml-3">
              <p className="text-sm text-green-800">{rebuildSuccess}</p>
            </div>
            <button
              onClick={() => setRebuildSuccess(null)}
              className="ml-auto text-green-400 hover:text-green-600"
            >
              ✕
            </button>
          </div>
        </div>
      )}


      {/* Loading Indicator */}
      {loading && (
        <div className="flex items-center justify-center p-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-gray-600">Loading...</span>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              placeholder="Search questions or answers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Categories</option>
              {/* Show all available categories including default ones */}
              {Array.from(new Set([
                ...categories,
                'general', 'office_information', 'appointments', 'pricing', 'insurance', 
                'payment', 'emergency_care', 'preventive_care', 'dental_procedures', 'cosmetic_dentistry',
                'pediatric_dentistry', 'patient_care', 'first_visit', 'oral_hygiene', 'nutrition',
                'dental_conditions', 'restorative_dentistry', 'orthodontics', 'oral_surgery', 'post_treatment_care',
                'special_populations'
              ])).sort().map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1).replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500">Total Entries</div>
          <div className="text-2xl font-bold text-gray-900">{filteredEntries.length}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500">Categories</div>
          <div className="text-2xl font-bold text-blue-600">
            {new Set(filteredEntries.map(entry => entry.category)).size}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm font-medium text-gray-500">RAG Ready</div>
          <div className="text-2xl font-bold text-green-600">
            {filteredEntries.filter(entry => entry.is_active && entry.embedding_vector).length}
          </div>
        </div>
      </div>

      {/* Q&A List */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="divide-y divide-gray-200">
          {filteredEntries.map((entry) => (
            <div key={entry.id} className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      entry.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {entry.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {entry.category}
                    </span>
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                      {entry.source}
                    </span>
                    {entry.is_active && entry.embedding_vector && (
                      <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-cyan-100 text-cyan-800">
                        <span className="w-2 h-2 bg-cyan-500 rounded-full mr-1"></span>
                        RAG Ready
                      </span>
                    )}
                  </div>
                  
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {entry.question}
                  </h3>
                  
                  <p className="text-gray-700 mb-3">
                    {entry.answer}
                  </p>
                  
                  <div className="text-sm text-gray-500">
                    Created: {new Date(entry.created_at).toLocaleDateString()} • 
                    Updated: {new Date(entry.updated_at).toLocaleDateString()}
                    {entry.source_url && (
                      <> • <a href={entry.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">Source</a></>
                    )}
                  </div>
                </div>
                
                <div className="flex space-x-2 ml-4">
                  <button
                    onClick={() => {
                      setEditingEntry(entry);
                      setIsEditing(true);
                    }}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-md"
                    title="Edit"
                    disabled={loading}
                  >
                    ✏️
                  </button>
                  
                  <button
                    onClick={() => handleDeleteEntry(entry.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                    title="Delete"
                    disabled={loading}
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {filteredEntries.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">No Q&A entries found matching your criteria.</div>
        </div>
      )}

      {/* Add Form Modal */}
      {showAddForm && (
        <QAForm
          onSubmit={handleAddEntry}
          onCancel={() => setShowAddForm(false)}
        />
      )}

      {/* Edit Form Modal */}
      {isEditing && editingEntry && (
        <QAForm
          entry={editingEntry}
          onSubmit={handleEditEntry}
          onCancel={() => {
            setIsEditing(false);
            setEditingEntry(null);
          }}
        />
      )}

      {/* RAG Test Modal */}
      {showQuickTest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🧪 RAG Vector Search Test</h3>
            <p className="text-sm text-gray-500 mb-4">
              Test how the RAG system retrieves relevant QA pairs from the knowledge base using FAISS vector search.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Test Query
                </label>
                <input
                  type="text"
                  value={testQuery}
                  onChange={(e) => setTestQuery(e.target.value)}
                  placeholder="e.g., How often should I brush my teeth?"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleQuickTest();
                    }
                  }}
                />
              </div>

              {/* RAG Test Results */}
              {ragTestResults && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">
                    🔍 RAG Search Results ({ragTestResults.results?.length || 0} matches)
                  </h4>
                  
                  {ragTestResults.error ? (
                    <div className="bg-red-50 border border-red-200 rounded p-3 mb-3">
                      <div className="flex items-center">
                        <span className="text-red-400 mr-2">❌</span>
                        <span className="text-red-800 text-sm">Error: {ragTestResults.error}</span>
                      </div>
                      <p className="text-red-600 text-xs mt-1">
                        Try rebuilding the vector database if search continues to fail.
                      </p>
                    </div>
                  ) : ragTestResults.results && ragTestResults.results.length > 0 ? (
                    <div className="space-y-3">
                      {ragTestResults.results.map((result: any, index: number) => (
                        <div key={index} className="bg-white p-3 rounded border">
                          <div className="flex justify-between items-start mb-2">
                            <h5 className="font-medium text-gray-900 text-sm">
                              {result.question}
                            </h5>
                            <div className="flex items-center space-x-2">
                              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                {result.category}
                              </span>
                              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                {(result.similarity_score * 100).toFixed(1)}% match
                              </span>
                              <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
                                ID: {result.kb_id}
                              </span>
                            </div>
                          </div>
                          <p className="text-gray-700 text-sm">{result.answer}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4">
                      <div className="text-gray-500 mb-2">
                        No matches found for "{ragTestResults.query}"
                      </div>
                      <div className="text-xs text-gray-400">
                        💡 Try a different query, or use the "Rebuild Vector DB" button to ensure all QA pairs are indexed
                      </div>
                    </div>
                  )}
                  
                  {ragTestResults.search_time && (
                    <div className="mt-3 text-xs text-gray-500">
                      Search completed in {ragTestResults.search_time}ms
                    </div>
                  )}
                </div>
              )}
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowQuickTest(false);
                    setTestQuery('');
                    setRagTestResults(null);
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Close
                </button>
                <button
                  onClick={handleQuickTest}
                  disabled={!testQuery.trim() || testingRAG}
                  className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                  {testingRAG ? '🔍 Searching...' : '🧪 Test RAG Search'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default QAEditor;