import React, { useState, useEffect } from 'react';
import { userAPI, faceAPI } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalAuthentications: 0,
    successRate: 0,
    recentActivity: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch users
      const usersResponse = await userAPI.getAll();
      const users = usersResponse.data.data.users;
      
      // Fetch recent authentication history
      const historyResponse = await faceAPI.getHistory({ limit: 10 });
      const history = historyResponse.data.data.history;
      
      // Calculate statistics
      const totalAuth = history.length;
      const successfulAuth = history.filter(log => log.success).length;
      const successRate = totalAuth > 0 ? (successfulAuth / totalAuth) * 100 : 0;
      
      setStats({
        totalUsers: users.length,
        totalAuthentications: totalAuth,
        successRate: successRate.toFixed(1),
        recentActivity: history.slice(0, 5)
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color }) => (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-3xl font-bold ${color}`}>{value}</p>
        </div>
        <div className={`text-4xl ${color}`}>{icon}</div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
      
      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Total Users"
          value={stats.totalUsers}
          icon="👥"
          color="text-primary-600"
        />
        <StatCard
          title="Total Authentications"
          value={stats.totalAuthentications}
          icon="🔐"
          color="text-green-600"
        />
        <StatCard
          title="Success Rate"
          value={`${stats.successRate}%`}
          icon="📊"
          color="text-blue-600"
        />
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
        {stats.recentActivity.length > 0 ? (
          <div className="space-y-3">
            {stats.recentActivity.map((activity, index) => (
              <div
                key={activity.id || index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    activity.success ? 'bg-green-100' : 'bg-red-100'
                  }`}>
                    {activity.success ? '✅' : '❌'}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {activity.success ? 'Successful' : 'Failed'} Authentication
                    </p>
                    <p className="text-sm text-gray-500">
                      {activity.user ? `${activity.user.name} (${activity.user.email})` : 'Unknown User'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">
                    {new Date(activity.timestamp).toLocaleString()}
                  </p>
                  {activity.confidence && (
                    <p className="text-xs text-gray-400">
                      Confidence: {(activity.confidence * 100).toFixed(1)}%
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No recent activity</p>
        )}
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a href="/users" className="card hover:shadow-xl transition-shadow duration-200 text-center">
            <div className="text-3xl mb-2">👤</div>
            <p className="font-medium text-gray-900">Add New User</p>
            <p className="text-sm text-gray-500">Register a new user in the system</p>
          </a>
          <a href="/register" className="card hover:shadow-xl transition-shadow duration-200 text-center">
            <div className="text-3xl mb-2">📸</div>
            <p className="font-medium text-gray-900">Register Face</p>
            <p className="text-sm text-gray-500">Add face data for existing users</p>
          </a>
          <a href="/authenticate" className="card hover:shadow-xl transition-shadow duration-200 text-center">
            <div className="text-3xl mb-2">🔓</div>
            <p className="font-medium text-gray-900">Test Authentication</p>
            <p className="text-sm text-gray-500">Try face authentication</p>
          </a>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;