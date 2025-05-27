import React, { useState, useEffect } from 'react';
import { faceAPI, userAPI } from '../services/api';

const History = () => {
  const [history, setHistory] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    userId: '',
    limit: 20
  });
  const [stats, setStats] = useState({
    total: 0,
    successful: 0,
    failed: 0,
    successRate: 0
  });

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch users for filter dropdown
      const usersResponse = await userAPI.getAll();
      setUsers(usersResponse.data.data.users);
      
      // Fetch history with filters
      const params = {};
      if (filters.userId) params.user_id = filters.userId;
      params.limit = filters.limit;
      
      const historyResponse = await faceAPI.getHistory(params);
      const historyData = historyResponse.data.data.history;
      setHistory(historyData);
      
      // Calculate statistics
      const successful = historyData.filter(log => log.success).length;
      const total = historyData.length;
      const successRate = total > 0 ? (successful / total) * 100 : 0;
      
      setStats({
        total,
        successful,
        failed: total - successful,
        successRate: successRate.toFixed(1)
      });
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString()
    };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Authentication History</h1>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <div className="text-sm text-gray-600">Total Attempts</div>
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-600">Successful</div>
          <div className="text-2xl font-bold text-green-600">{stats.successful}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-600">Failed</div>
          <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-600">Success Rate</div>
          <div className="text-2xl font-bold text-blue-600">{stats.successRate}%</div>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by User
            </label>
            <select
              value={filters.userId}
              onChange={(e) => handleFilterChange('userId', e.target.value)}
              className="input-field"
            >
              <option value="">All Users</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.email})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Records
            </label>
            <select
              value={filters.limit}
              onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
              className="input-field"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={fetchData}
              className="btn-primary w-full"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* History Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.map((log, index) => {
                const { date, time } = formatTimestamp(log.timestamp);
                return (
                  <tr key={log.id || index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          log.success ? 'bg-green-100' : 'bg-red-100'
                        }`}>
                          {log.success ? '✅' : '❌'}
                        </div>
                        <span className={`ml-2 text-sm font-medium ${
                          log.success ? 'text-green-800' : 'text-red-800'
                        }`}>
                          {log.success ? 'Success' : 'Failed'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {log.user ? (
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {log.user.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {log.user.email}
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">Unknown</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {log.confidence ? (
                        <div className="flex items-center">
                          <div className="text-sm text-gray-900">
                            {(log.confidence * 100).toFixed(1)}%
                          </div>
                          <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${log.confidence * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {date}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {time}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          
          {history.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No authentication history found
            </div>
          )}
        </div>
      </div>

      {/* Export Options */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={() => {
            const csvContent = [
              ['Status', 'User Name', 'User Email', 'Confidence', 'Date', 'Time'],
              ...history.map(log => {
                const { date, time } = formatTimestamp(log.timestamp);
                return [
                  log.success ? 'Success' : 'Failed',
                  log.user?.name || 'Unknown',
                  log.user?.email || '-',
                  log.confidence ? `${(log.confidence * 100).toFixed(1)}%` : '-',
                  date,
                  time
                ];
              })
            ].map(row => row.join(',')).join('\n');
            
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `authentication_history_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
          }}
          className="btn-outline"
        >
          Export to CSV
        </button>
      </div>
    </div>
  );
};

export default History;